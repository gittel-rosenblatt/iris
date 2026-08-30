import os
from datetime import timedelta, datetime, timezone
from dotenv import load_dotenv
from flask import Flask, flash, redirect, render_template, request, session, url_for, jsonify
from flask_mailman import EmailMultiAlternatives, Mail
from flask_sqlalchemy import SQLAlchemy
from itsdangerous import URLSafeTimedSerializer
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=6)
app.config['SESSION_REFRESH_EACH_REQUEST'] = True

serializer = URLSafeTimedSerializer(app.secret_key)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///iris.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['MAIL_SERVER'] = 'sandbox.smtp.mailtrap.io'
app.config['MAIL_PORT'] = 2525
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'

db = SQLAlchemy(app)
mail = Mail()
mail.init_app(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    avatar = db.Column(db.String(100), default='default-pfp.png')

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

class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    filename = db.Column(db.String(225), nullable=False)
    status = db.Column(db.String(20), default='draft')
    data_json = db.Column(db.JSON, nullable=True)

STATES = [
        "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
        "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
        "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
        "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
        "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"
    ]

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
            session.permanent = True
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

        user_check = User.query.filter_by(username=username).first()
        email_check = User.query.filter_by(email=email).first()
        
        if user_check or email_check:
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

    user_projects = None
    # user_projects will = a list of the user's projects ;)

    return render_template('dashboard.html', user=current_user, first_name=current_user.first_name, username=current_user.username, projects=user_projects) 
    
@app.route('/workspace')
def workspace():
    if 'user' not in session:
        return redirect(url_for('login'))

    current_user = User.query.filter_by(username=session['user']).first()
    
    return render_template('workspace.html', user=current_user) 

@app.route('/profile')
def profile():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    current_user = User.query.filter_by(username=session['user']).first()

    required_fields = [
        current_user.first_name,
        current_user.last_name,
        current_user.middle_initial,
        current_user.birthday,
        current_user.phone,
        current_user.street,
        current_user.city,
        current_user.state,
        current_user.zip_code
    ]

    is_complete = all(required_fields)

    return render_template('profile.html', user=current_user, states=STATES, profile_is_complete=is_complete)
    
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

    def clean_input(field_name):
        value = request.form.get(field_name, '').strip()
        return value if value else None

    current_user = User.query.filter_by(username=session['user']).first()
    selected_avatar = request.form.get('avatar')

    email = request.form.get('email', '').strip().lower()
    email_check = User.query.filter_by(email=email).first()

    if email_check and email_check.id != current_user.id:
        flash(f"Email is already in use.", "danger")
        return redirect(url_for('profile'))
    
    current_user.email = email
    current_user.avatar = selected_avatar
    current_user.first_name = clean_input('first_name')
    current_user.last_name = clean_input('last_name')
    current_user.middle_initial = clean_input('middle_initial')
    current_user.phone = clean_input('phone')
    current_user.birthday = clean_input('dob')
    current_user.street = clean_input('street')
    current_user.city = clean_input('city')
    current_user.state = clean_input('state')
    current_user.zip_code = clean_input('zip')

    db.session.commit()

    flash('Account updated successfully!', 'success')
    return redirect(url_for('profile'))

@app.route('/update-password', methods=['POST'])
def update_password():
    if 'user' not in session:
        return redirect(url_for('login'))

    current_user = User.query.filter_by(username=session['user']).first()

    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')

    if  not check_password_hash(current_user.password_hash, current_password):
        flash('Incorrect password. Please try again.', 'password_error')
        return redirect(url_for('profile', modal='password'))

    if new_password != confirm_password:
        flash('Passwords do not match. Please try again.', 'password_error')
        return redirect(url_for('profile', modal='password'))

    hashed_password = generate_password_hash(new_password, method='pbkdf2:sha256')
    current_user.password_hash = hashed_password

    db.session.commit()
    flash('Password updated successfully!', 'profile_success')
    return redirect(url_for('profile'))

@app.route('/keep-alive', methods=['POST'])
def keep_alive():
    session.modified = True  
    return jsonify({"status": "session_extended"})

@app.route('/upload-endpoint', methods=['POST'])
def upload():
    if 'user' not in session:
        return redirect(url_for('login'))

    pdf_check = request.files.get("pdf_file")
    pdf = ''

    if pdf_check and pdf_check.filename != "":
        first_bytes = pdf_check.read(4)
        pdf_check.seek(0)

        is_valid_ext = pdf_check.filename.lower().endswith('.pdf')
        is_valid_mime = pdf_check.content_type == 'application/pdf'
        is_valid_bytes = first_bytes == b'%PDF' 

        if is_valid_ext and is_valid_mime and is_valid_bytes:
            pdf = pdf_check

            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            
            filename = secure_filename(pdf.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            pdf.save(file_path)
            
        else:
            flash("Upload is not a valid PDF. Please try again.", "danger")
            return redirect(url_for('dashboard'))
    else:
        flash("No file was selected.", "danger")
        return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True)