import os

from dotenv import load_dotenv
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_mailman import EmailMultiAlternatives, Mail
from flask_sqlalchemy import SQLAlchemy
from itsdangerous import URLSafeTimedSerializer
from werkzeug.security import check_password_hash, generate_password_hash

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

serializer = URLSafeTimedSerializer(app.secret_key)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///iris.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['MAIL_SERVER'] = 'sandbox.smtp.mailtrap.io'
app.config['MAIL_PORT'] = 2525
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False

db = SQLAlchemy(app)
mail = Mail()
mail.init_app(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)

    email = db.Column(db.String(120), unique=True, nullable=False)

    first_name = db.Column(db.String(50), nullable=True)
    last_name = db.Column(db.String(50), nullable=True)
    middle_initial = db.Column(db.String(1), nullable=True)

    birthday = db.Column(db.String(15), nullable=True)

    phone = db.Column(db.String(20), nullable=True)

    street = db.Column(db.String(120), nullable=True)
    city = db.Column(db.String(50), nullable=True)
    state = db.Column(db.String(2), nullable=True)
    zip_code = db.Column(db.String(10), nullable=True)

with app.app_context():
    db.create_all()

@app.route("/")
def home():
    return render_template("index.html")

@app.route('/our-story')
def story():
    return render_template('story.html') 
    
@app.route('/terms-of-service')
def terms():
    return render_template('terms.html') 

@app.route('/privacy-policy')
def privacy():
    return render_template('privacy.html') 

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email_username = request.form.get('username')
        password = request.form.get('password')

        found_user = User.query.filter_by(username=email_username).first()
        if not found_user:
            found_user = User.query.filter_by(email=email_username).first()

        if found_user and check_password_hash(found_user.password_hash, password):
            session['user'] = found_user.username
            flash("Account logged in successfully!", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Something went wrong. Please try again.", "danger")
            return render_template('login.html')
    
    return render_template('login.html') 

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username').strip()
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        email = request.form.get('email').strip().lower() 

        user = User.query.filter_by(username=username).first()
        email_check = User.query.filter_by(email=email).first()
        
        if user or email_check:
            flash(f"Username or email already in use. Please log in.", "danger")
            return redirect(url_for('signup'))
        elif password != confirm_password:
            flash(f"Passwords to not match. Please try again.", "danger")
            return redirect(url_for('signup'))

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        new_user = User(username=username, password_hash=hashed_password, email=email)

        db.session.add(new_user)
        db.session.commit()

        flash('Account created successfully! You can now log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('signup.html')

@app.route("/forgot-password", methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        target_input = request.form.get('username')

        user = User.query.filter_by(username=target_input).first()
        if not user: 
            user = User.query.filter_by(email=target_input).first()

        if user:
            token = serializer.dumps(user.email, salt='password-reset-salt')
            reset_url = url_for('reset_password', token=token, _external=True)
            
            msg = EmailMultiAlternatives(
                "Password Reset Request",
                f"Hello,\n\nTo reset your password, click the following link:\n{reset_url}\n\nThis link will expire in 15 minutes.",
                "noreply@yourdomain.com",
                [user.email]
            )

            html_content = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <style>
                        @import url('https://googleapis.com');
                    </style>
                </head>
                <body style="margin: 0; padding: 0; background-color: #ffffff;">
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
            
            msg.attach_alternative(html_content, "text/html")
            msg.send()

            flash("A password reset link has been sent. Please check your inbox and your spam folder!", "info")
            return redirect(url_for('login'))
        else: 
            flash("We couldn't find an account with that username or email address. Please try again.", "danger")
            return redirect(url_for('forgot_password'))
        
    return render_template("forgot-password.html") 

@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    try:
        email = serializer.loads(token, salt='password-reset-salt', max_age=900)
    except Exception:
        email = None

    if not email:
        flash("Token is expired. Please try again.", "warning")
        return redirect(url_for('forgot_password'))

    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if password != confirm_password:
            flash(f"Passwords to not match. Please try again.", "danger")
            return redirect(url_for('reset_password', token=token))
        else: 
            user_to_update = User.query.filter_by(email=email).first()

            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
            user_to_update.password_hash = hashed_password
            db.session.commit()

            flash("Password updated successfully! Please login.", "success")
            return redirect(url_for("login"))

    return render_template('reset-password.html', token=token)

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))

    current_user = User.query.filter_by(username=session['user']).first()

    return render_template('dashboard.html', first_name=current_user.first_name, username=current_user.username) 
    
@app.route('/workspace')
def workspace():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    return render_template('workspace.html') 

@app.route('/profile')
def profile():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    return render_template('profile.html') 

@app.route("/contact-and-faqs")
def contact():
    return render_template("contact.html") 

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route('/update-profile', methods=['POST'])
def update_profile():
    if 'user' not in session:
        return redirect(url_for('login'))

    return redirect(url_for('profile'))

@app.route('/update-password', methods=['POST'])
def update_password():
    if 'user' not in session:
        return redirect(url_for('login'))

    return redirect(url_for('profile'))

if __name__ == "__main__":
    app.run(debug=True)