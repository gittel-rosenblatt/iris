import hashlib
import hmac
import resend
import os

from cryptography.fernet import Fernet
from extensions import db, serializer
from flask import Blueprint, flash, redirect, render_template, request, session, url_for, jsonify, g
from flask_mailman import EmailMultiAlternatives
from models import User, login_required
from werkzeug.security import check_password_hash, generate_password_hash

auth_bp = Blueprint('auth', __name__)

resend.api_key = os.environ.get("RESEND_API_KEY")

email_hash = os.getenv('EMAIL_HASH_KEY')
email_hash_key = email_hash.encode('utf-8')

encryption_key = os.getenv('ENCRYPTION_KEY')
cipher = Fernet(encryption_key.encode()) if encryption_key else None

def generate_email_hash(email: str) -> str:
    clean_email = email.strip().lower().encode('utf-8')
    
    email_hash = hmac.new(email_hash_key, clean_email, hashlib.sha256).hexdigest()
    
    return email_hash

def encrypt(value):
    if value:
        encrypted_bytes = cipher.encrypt(value.encode())
        return encrypted_bytes.decode()
    return None

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username').strip()
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        email = request.form.get('email').strip().lower() 

        user_check = User.query.filter_by(username=username).first()

        searchable_hash = generate_email_hash(email)
        existing_user = User.query.filter_by(email_hash=searchable_hash).first()
        
        if user_check or existing_user:
            flash(f"Username or email already in use. Please log in.", "danger")
            return redirect(url_for('auth.signup'))
        elif password != confirm_password:
            flash(f"Passwords to not match. Please try again.", "danger")
            return redirect(url_for('auth.signup'))
        elif not request.form.get('agree_terms'):
            flash("You must agree to the Terms of Service to create an account.")
            return redirect(url_for('auth.signup'))

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        email_hash = generate_email_hash(email)
        email_encrypted = encrypt(email)

        new_user = User(username=username, password_hash=hashed_password, email_hash=email_hash, email_encrypted=email_encrypted)

        db.session.add(new_user)
        db.session.commit()

        flash('Account created successfully! You can now log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('signup.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email_username = request.form.get('username')
        password = request.form.get('password')

        found_user = User.query.filter_by(username=email_username).first()
        if not found_user:
            searchable_hash = generate_email_hash(email_username)
            found_user = User.query.filter_by(email_hash=searchable_hash).first()

        if found_user and check_password_hash(found_user.password_hash, password):
            session['user_id'] = found_user.id  
            session['user'] = found_user.username 
            session.permanent = True
            flash("Account logged in successfully!", "success")
            return redirect(url_for('dashboard.dashboard'))
        else:
            flash("Something went wrong. Please try again.", "danger")
            return render_template('login.html')
    
    return render_template('login.html') 

@auth_bp.route("/forgot-password", methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        target_input = request.form.get('username')

        user = User.query.filter_by(username=target_input).first()
        if not user: 
            searchable_hash = generate_email_hash(target_input)
            user = User.query.filter_by(email_hash=searchable_hash).first()

        if user:
            email = user.decrypted_email
            token = serializer.dumps(user.email_hash, salt='password-reset-salt')
            reset_url = url_for('auth.reset_password', token=token, _external=True)
            
            # msg = EmailMultiAlternatives(
            #     "Password Reset Request",
            #     f"Hello,\n\nTo reset your password, click the following link:\n{reset_url}\n\nThis link will expire in 15 minutes.",
            #     "noreply@yourdomain.com",
            #     [user.email]
            # )

            html_content = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <style>
                        @import url('https://googleapis.com');
                    </style>
                </head>
                <body style="margin: 0; padding: 0; background-color: #FAF7F2;">
                    <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%">
                        <tr>
                            <td style="padding: 40px 30px;"> 
                                
                                <p style="margin: 0 0 20px 0; font-family: 'Atkinson Hyperlegible', Arial, sans-serif; font-size: 24px; color: #371961; line-height: 1.5;">
                                    Hello,
                                </p>
                                <p style="margin: 0 0 20px 0; font-family: 'Atkinson Hyperlegible', Arial, sans-serif; font-size: 24px; color: #371961; line-height: 1.5;">
                                    To reset your password, click the button below:
                                </p>
                                <p style="margin: 30px 0;">
                                    <a href="{reset_url}" style="
                                        font-family: 'Atkinson Hyperlegible', Arial, sans-serif;
                                        font-size: 24px;
                                        font-weight: bold;
                                        background-color: #E6DCF5;
                                        color: #5522A6;
                                        padding: 15px 30px;
                                        text-decoration: none;
                                        border-radius: 8px;
                                        border: 4px solid #5522A6;
                                        display: inline-block;
                                    ">
                                        Reset Password
                                    </a>
                                </p>
                                <p style="margin: 0; font-family: 'Atkinson Hyperlegible', Arial, sans-serif; font-size: 24px; color: #371961; line-height: 1.5;">
                                    This link will expire in 15 minutes.
                                </p>
                                
                            </td>
                        </tr>
                    </table>
                </body>
                </html>
                """
            try:
                params = {
                    "from": "Iris <noreply@irisforms.org>", 
                    "to": [email],
                    "subject": "Password Reset Request - Iris",
                    "html": html_content
                }
                resend.Emails.send(params)
                flash("A password reset link has been sent. Please check your inbox and your spam folder!", "info")
            except Exception as e:
                print(f"Resend API Error: {e}")
                flash("There was an error sending your password reset email. Please try again later.", "danger")

            return redirect(url_for('auth.login'))
        else: 
            flash("We couldn't find an account with that username or email address. Please try again.", "danger")
            return redirect(url_for('auth.forgot_password'))
        
    return render_template("forgot-password.html")

@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    try:
        email = serializer.loads(token, salt='password-reset-salt', max_age=900)
    except Exception:
        email = None

    if not email:
        flash("Token is expired. Please try again.", "warning")
        return redirect(url_for('auth.forgot_password'))

    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if password != confirm_password:
            flash(f"Passwords to not match. Please try again.", "danger")
            return redirect(url_for('auth.reset_password', token=token))
        else: 
            user_to_update = User.query.filter_by(email_hash=email).first()

            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
            user_to_update.password_hash = hashed_password
            db.session.commit()

            flash("Password updated successfully! Please login.", "success")
            return redirect(url_for("auth.login"))

    return render_template('reset-password.html', token=token)

@auth_bp.route('/logout')
@login_required
def logout():
    session.clear() 
    flash("You have been logged out.", "info")
    return redirect(url_for('auth.login'))

@auth_bp.route('/keep-alive', methods=['POST'])
@login_required
def keep_alive():
    session.modified = True  
    return jsonify({"status": "session_extended"})