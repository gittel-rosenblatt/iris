import fitz
import json
import os
import re
import time
import uuid

from cryptography.fernet import Fernet
from datetime import timedelta, datetime, date, timezone
from dotenv import load_dotenv
from flask import Flask, flash, redirect, render_template, request, send_file, session, url_for, jsonify, g
from flask_mailman import EmailMultiAlternatives, Mail
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
from google import genai
from google.genai import types
from itsdangerous import URLSafeTimedSerializer
from pypdf import PdfReader, PdfWriter
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

encryption_key = os.getenv('ENCRYPTION_KEY')
cipher = Fernet(encryption_key.encode()) if encryption_key else None

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

    first_name = db.Column(db.Text, nullable=True)
    last_name = db.Column(db.Text, nullable=True)
    middle_initial = db.Column(db.Text, nullable=True)

    birthday = db.Column(db.Text, nullable=True)

    phone = db.Column(db.Text, nullable=True)

    street = db.Column(db.Text, nullable=True)
    city = db.Column(db.Text, nullable=True)
    state = db.Column(db.Text, nullable=True)
    zip_code = db.Column(db.Text, nullable=True)

    def _decrypt(self, value):
        if value:
            try:
                return cipher.decrypt(value.encode()).decode()
            except Exception:
                return value
        return ''

    @property
    def decrypted_first_name(self):
        return self._decrypt(self.first_name)

    @property
    def decrypted_last_name(self):
        return self._decrypt(self.last_name)

    @property
    def decrypted_middle_initial(self):
        return self._decrypt(self.middle_initial)

    @property
    def decrypted_birthday(self):
        return self._decrypt(self.birthday)

    @property
    def decrypted_phone(self):
        return self._decrypt(self.phone)

    @property
    def decrypted_street(self):
        return self._decrypt(self.street)

    @property
    def decrypted_city(self):
        return self._decrypt(self.city)

    @property
    def decrypted_state(self):
        return self._decrypt(self.state)

    @property
    def decrypted_zip_code(self):
        return self._decrypt(self.zip_code)

class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    filename = db.Column(db.String(225), nullable=False)
    status = db.Column(db.String(20), default='draft')
    data_json = db.Column(db.Text, nullable=True)

    original_file_path = db.Column(db.String(300), nullable=False)
    completed_file_path = db.Column(db.String(300), nullable=True)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

@app.template_filter('isoformat_utc')
def isoformat_utc(dt):
    if not dt:
        return ""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.isoformat()

def parse_pdf_with_gemini(filepath):
    """
    Takes a path to a saved PDF file, uploads it to 
    Gemini, and returns a parsed list of form fields 
    as Python data (dictionaries/lists).
    """

    max_retries = 3
    delay = 2 

    client = genai.Client()
    
    uploaded_file = client.files.upload(file=filepath)
    
    prompt = """
    You are an expert document parser. Scan and analyze this form from top to bottom and extract 
    EVERY single fillable field, label, checkbox, and table row (including repeating structures 
    like Dependents, W-2 lines, or itemized lists).

    Return a JSON array of objects, where each object has:
    1. "field_label": The question or prompt text (e.g., 'First Name', 'Date of Birth')
    2. "field_type": The type of input required ('text', 'date', 'checkbox', 'signature', 'numeric', etc.)
    3. "field_options": For checkboxes or multiple-choice fields, an array of options; otherwise null.
    4. "is_required": A boolean indicating if the field is required or optional.
    5. "page": The 0-indexed page number where the field appears (e.g., 0 for page 1).
    6. "box_2d": The exact normalized 2D bounding box coordinates [ymin, xmin, ymax, xmax] on a scale of 0 to 1000 representing the exact input line or box area.
    """

    for attempt in range(max_retries):
        try:
            print(f"Attempt {attempt + 1} to parse PDF with Gemini API...")
            response = client.models.generate_content(
                model="gemini-3.5-flash",
                contents=[uploaded_file, prompt],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )
            parsed_data = json.loads(response.text)
            return parsed_data

        except Exception as e:
            if "503" in str(e) or "UNAVAILABLE" in str(e):
                if attempt < max_retries - 1:
                    time.sleep(delay)
                    delay *= 2  
                    continue
            raise e

def extract_acroform_fields(filepath):
    questions = []
    doc = fitz.open(filepath)
    
    for page_num, page in enumerate(doc):
        words = page.get_text("words") 
        for widget in page.widgets():
            if widget.field_flags & 1:
                continue

            rect = widget.rect
            if rect.width == 0 or rect.height == 0:
                continue

            display_label = (widget.field_label or "").strip()

            if not display_label or "topmostSubform" in display_label or display_label.startswith("F1"):
                nearby_words = []
                for w in words:
                    wx0, wy0, wx1, wy1, text = w[0], w[1], w[2], w[3], w[4]
                    
                    if (rect.x0 - 150 <= wx0 <= rect.x1) and (rect.y0 - 25 <= wy0 <= rect.y1):
                        nearby_words.append((wy0, wx0, text))

                if nearby_words:
                    nearby_words.sort(key=lambda item: (item[0], item[1]))
                    extracted_text = " ".join([w[2] for w in nearby_words if len(w[2]) > 1])
                    if len(extracted_text) > 3:
                        display_label = extracted_text

            if not display_label or display_label.startswith("F1"):
                raw = widget.field_name.split(".")[-1].replace("[0]", "")
                display_label = raw.replace("_", " ").title()

            w_type = widget.field_type_string.lower()
            if "checkbox" in w_type:
                normalized_type = "checkbox"
            elif "radio" in w_type:
                normalized_type = "radio"
            elif "combo" in w_type or "list" in w_type:
                normalized_type = "select"
            else:
                normalized_type = "text"

            questions.append({
                "id": widget.field_name,
                "field_label": display_label,
                "field_type": normalized_type,
                "field_options": widget.choice_values or [],
                "field_required": bool(widget.field_flags & 2),
                "page": page_num,
                "field_answer": widget.field_value or ""
            })

    doc.close()
    return questions

@app.route('/save', methods=['POST'])
def save_answers(original_file_path, completed_file_path, user_answers, form_type="acroform", items_list=None):
    if not os.path.exists(original_file_path):
        raise FileNotFoundError(f"Cannot find original PDF at {original_file_path}")

    doc = fitz.open(original_file_path)
    
    if form_type == "acroform":
        for page in doc:
            for widget in page.widgets():
                if widget.field_name in user_answers:
                    user_val = user_answers[widget.field_name]
                    
                    # Checkbox / Radio handling
                    if widget.field_type_string in ["CheckBox", "RadioButton"]:
                        if user_val and user_val not in [False, "False", "Off", ""]:
                            # Grab the exact 'ON' value expected by this PDF form field
                            on_val = widget.on_state() or "Yes"
                            widget.field_value = on_val
                        else:
                            widget.field_value = "Off"
                    else:
                        # Standard Text / Select handling
                        widget.field_value = str(user_val or "")
                        
                    widget.update()
                    
    else:
        items_list = items_list or []
        for item in items_list:
            page_num = item.get("page", 0)
            if page_num < 0 or page_num >= len(doc):
                page_num = 0
                
            page = doc[page_num]
            page_w = page.rect.width
            page_h = page.rect.height

            field_id = item.get("id") or item.get("field_label")
            user_val = user_answers.get(field_id)

            if item.get("field_type") == "checkbox":
                text_to_print = "X" if user_val else ""
            else:
                text_to_print = str(user_val or "")

            if re.match(r"^\d{4}-\d{2}-\d{2}$", text_to_print):
                parts = text_to_print.split("-")
                text_to_print = f"{parts[1]}/{parts[2]}/{parts[0]}"
    
            if not text_to_print:
                continue
    
            box = item.get("box_2d") or item.get("bbox")
            
            if box and len(box) == 4:
                ymin, xmin, ymax, xmax = box
                
                rect_xmin = (xmin / 1000.0) * page_w
                rect_ymin = (ymin / 1000.0) * page_h
                rect_xmax = (xmax / 1000.0) * page_w
                rect_ymax = (ymax / 1000.0) * page_h
                
                if item.get("field_type") == "checkbox":
                    fit_x = rect_xmin + ((rect_xmax - rect_xmin) / 4)
                    fit_y = rect_ymax - ((rect_ymax - rect_ymin) / 4)
                    page.insert_text(fitz.Point(fit_x, fit_y), "X", fontsize=10, color=(0, 0, 0))
                else:
                    fit_x = rect_xmin + 4
                    fit_y = rect_ymax - 3
                    page.insert_text(fitz.Point(fit_x, fit_y), text_to_print, fontsize=8.5, color=(0, 0, 0))
            else:
                raw_x = item.get("x", 0)
                raw_y = item.get("y", 0)
                
                fit_x = (raw_x / 1000.0) * page_w if raw_x > page_w else raw_x
                fit_y = (raw_y / 1000.0) * page_h if raw_y > page_h else raw_y
                
                page.insert_text(fitz.Point(fit_x + 5, fit_y + 10), text_to_print, fontsize=8.5, color=(0, 0, 0))
        
    doc.save(completed_file_path)
    doc.close()
            
    return jsonify({"status": "success"})

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        
        current_user = User.query.filter_by(username=session['user']).first()
        if not current_user:
            session.clear()
            return redirect(url_for('login'))
            
        g.current_user = current_user
        return f(*args, **kwargs)
    return decorated_function

@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response

@app.context_processor
def inject_user():
    return dict(current_user=getattr(g, 'current_user', None))

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
            session['user_id'] = found_user.id  
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
@login_required
def dashboard():
    current_user = g.current_user

    total_active_docs = Document.query.filter_by(user_id=current_user.id).count()
    uploads_left = max(0, 5 - total_active_docs)

    user_projects = Document.query.filter_by(user_id=current_user.id).order_by(Document.created_at.desc()).all()

    return render_template('dashboard.html', 
                           user=current_user, 
                           first_name=current_user.first_name, 
                           username=current_user.username, 
                           projects=user_projects, 
                           uploads_left=uploads_left)

@app.route('/workspace/<int:doc_id>')
@login_required
def workspace(doc_id):
    current_user = g.current_user

    doc = Document.query.filter_by(id=doc_id, user_id=current_user.id).first()

    if not doc:
        flash("Document not found or access denied.", "danger")
        return redirect(url_for('dashboard'))

    raw_json = cipher.decrypt(doc.data_json.encode()).decode()
    parsed_fields = json.loads(raw_json)

    return render_template('workspace.html', 
                           user=current_user, 
                           document=doc,
                           fields=parsed_fields)

@app.route('/profile')
@login_required
def profile():
    current_user = g.current_user

    fields = [
        current_user.decrypted_first_name,
        current_user.decrypted_last_name,
        current_user.decrypted_middle_initial,
        current_user.decrypted_birthday,
        current_user.decrypted_phone,
        current_user.decrypted_street,
        current_user.decrypted_city,
        current_user.decrypted_state,
        current_user.decrypted_zip_code
    ]

    is_complete = all(fields)

    return render_template('profile.html', 
                           user=current_user, 
                           states=STATES, 
                           profile_is_complete=is_complete)
    
@app.route("/contact-and-faqs")
def contact():
    return render_template("contact.html") 

@app.route('/logout')
def logout():
    session.clear() 
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))

@app.route('/update-profile', methods=['POST'])
@login_required
def update_profile():
    current_user = g.current_user 

    def clean_input(field_name):
        value = request.form.get(field_name, '').strip()
        return value if value else None

    def encrypt(value):
        if value:
            encrypted_bytes = cipher.encrypt(value.encode())
            return encrypted_bytes.decode()
        return None

    selected_avatar = request.form.get('avatar')

    email = request.form.get('email', '').strip().lower()
    email_check = User.query.filter_by(email=email).first()

    if email_check and email_check.id != current_user.id:
        flash(f"Email is already in use.", "danger")
        return redirect(url_for('profile'))
    
    current_user.email = email
    current_user.avatar = selected_avatar
    current_user.first_name = encrypt(clean_input('first_name'))
    current_user.last_name = encrypt(clean_input('last_name'))
    current_user.middle_initial = encrypt(clean_input('middle_initial'))
    current_user.phone = encrypt(clean_input('phone'))
    current_user.birthday = encrypt(clean_input('dob'))
    current_user.street = encrypt(clean_input('street'))
    current_user.city = encrypt(clean_input('city'))
    current_user.state = encrypt(clean_input('state'))
    current_user.zip_code = encrypt(clean_input('zip'))

    db.session.commit()

    flash('Account updated successfully!', 'success')
    return redirect(url_for('profile'))

@app.route('/update-password', methods=['POST'])
@login_required
def update_password():
    current_user = g.current_user

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
@login_required
def upload(): 
    current_user = g.current_user

    pdf_check = request.files.get("pdf_file")
    pdf = ''

    total_active_docs = Document.query.filter_by(user_id=current_user.id).count()

    if total_active_docs >= 5:
        flash("You have reached your limit of 5 stored documents! Please delete an existing project to free up a slot.", "warning")
        return redirect(url_for('dashboard'))

    if pdf_check and pdf_check.filename != "":        
        first_bytes = pdf_check.read(4)
        pdf_check.seek(0)

        is_valid_ext = pdf_check.filename.lower().endswith('.pdf')
        is_valid_mime = pdf_check.content_type == 'application/pdf'
        is_valid_bytes = first_bytes == b'%PDF' 

        if is_valid_ext and is_valid_mime and is_valid_bytes:
            pdf = pdf_check

            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            
            safe_name = secure_filename(pdf.filename)
            unique_filename = f"{uuid.uuid4().hex[:8]}_{safe_name}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)

            pdf.save(file_path)

            doc_check = fitz.open(file_path)
            is_acroform = any(len(list(page.widgets())) > 0 for page in doc_check)
            doc_check.close()

            if is_acroform:
                try:
                    parsed_fields = extract_acroform_fields(file_path)
                except Exception as e:
                    flash("There was an error processing your document. Please try again in a moment!", "warning")
                    return redirect(url_for('dashboard'))
            else:
                try:
                    parsed_fields = parse_pdf_with_gemini(file_path)
                except Exception as e:
                    flash("Gemini API is temporarily experiencing high demand. Please try again in a moment!", "warning")
                    return redirect(url_for('dashboard'))

            json_string = json.dumps(parsed_fields)
            encrypted_bytes = cipher.encrypt(json_string.encode())
            encrypted_string = encrypted_bytes.decode()

            new_doc = Document(
                user_id=current_user.id,
                filename=unique_filename,
                status='draft',
                data_json=encrypted_string,
                original_file_path = file_path
            )

            db.session.add(new_doc)
            db.session.commit()

            flash("PDF uploaded and parsed successfully!", "success")
            return redirect(url_for('workspace', doc_id=new_doc.id))
            
        else:
            flash("Upload is not a valid PDF. Please try again.", "danger")
            return redirect(url_for('dashboard'))
    else:
        flash("No file was selected.", "danger")
        return redirect(url_for('dashboard'))
    
@app.route('/send-contact', methods=['POST'])
def send_contact():
    name = request.form.get('name')
    sender_email = request.form.get('email')
    message_body = request.form.get('message')

    msg = EmailMultiAlternatives(
        subject=f"Iris Contact Form: Message from {name}",
        body=f"Name: {name}\nEmail: {sender_email}\n\nMessage:\n{message_body}",
        from_email="noreply@irisapp.com",
        to=["iris@gmail.com"],
        headers={'Reply-To': sender_email}
    )
    
    try:
        msg.send()
        flash("Thank you for reaching out! Your message has been sent.", "success")
    except Exception as e:
        flash("There was an error sending your message. Please try again.", "danger")

    return redirect(url_for('contact'))

@app.route('/delete-document/<int:doc_id>', methods=['POST'])
@login_required
def delete_document(doc_id):
    current_user = g.current_user 

    doc = Document.query.filter_by(id=doc_id, user_id=current_user.id).first()

    if doc:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], doc.filename)
        if os.path.exists(file_path):
            os.remove(file_path)

        db.session.delete(doc)
        db.session.commit()
        flash("Project deleted successfully.", "info")
    else:
        flash("Document not found or access denied.", "danger")

    return redirect(url_for('dashboard'))

@app.route('/project/<int:doc_id>/submit', methods=['POST'])
@login_required
def submit(doc_id):
    current_user = g.current_user
    doc = Document.query.filter_by(id=doc_id, user_id=current_user.id).first_or_404()

    original_path = doc.original_file_path
    completed_path = os.path.join(app.config['UPLOAD_FOLDER'], f"filled_{doc.id}.pdf")
    doc.completed_file_path = completed_path

    raw_json = cipher.decrypt(doc.data_json.encode()).decode()
    fields = json.loads(raw_json)

    user_answers = {}
    for i, field in enumerate(fields, start=1):
        key = f"answer-{i}"
        
        if field.get('field_type') == 'checkbox':
            ans = True if request.form.get(key) else False
        else:
            ans = request.form.get(key, '')

        field['field_answer'] = ans
        
        field_name = field.get('id') or field.get('field_label')
        user_answers[field_name] = ans

    save_answers(original_path, completed_path, user_answers, form_type="acroform")

    doc.status = 'under_review'
    updated_json = json.dumps(fields)
    doc.data_json = cipher.encrypt(updated_json.encode()).decode()
    db.session.commit()

    return render_template('review_doc.html', 
                           user=current_user, 
                           document=doc, 
                           fields=fields)

@app.route('/project/<int:doc_id>/submit/view_pdf', methods=['GET', 'POST'])
@login_required
def view_pdf(doc_id):
    print(f"Made it to view_pdf route for doc_id: {doc_id}")

    current_user = g.current_user
    
    doc = Document.query.filter_by(id=doc_id, user_id=current_user.id).first_or_404()

    raw_json = cipher.decrypt(doc.data_json.encode()).decode()
    fields = json.loads(raw_json)

    return render_template(
        'view_pdf.html', 
        user=current_user, 
        document=doc, 
        fields=fields
    )

@app.route('/project/<int:doc_id>/pdf_file')
@login_required
def serve_pdf(doc_id):
    doc = Document.query.get_or_404(doc_id)
    return send_file(doc.completed_file_path, mimetype='application/pdf')

@app.route('/project/<int:doc_id>')
@login_required
def open_project(doc_id):
    doc = Document.query.filter_by(id=doc_id, user_id=g.current_user.id).first_or_404()
    
    if doc.status == 'under_review':
        return redirect(url_for('view_pdf', doc_id=doc.id))
    elif doc.status == 'completed':
        return redirect(url_for('view_pdf', doc_id=doc.id))
    else:
        return redirect(url_for('workspace', doc_id=doc.id))

if __name__ == '__main__':
    app.run(debug=True)