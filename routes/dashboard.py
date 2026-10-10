import os

from extensions import db, cipher
from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for, g
from models import User, Document, login_required
from werkzeug.security import check_password_hash, generate_password_hash

dashboard_bp = Blueprint('dashboard', __name__)

STATES = [
        "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
        "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
        "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
        "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
        "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"
    ] 

@dashboard_bp.route('/dashboard')
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

@dashboard_bp.route('/profile')
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

@dashboard_bp.route('/update-profile', methods=['POST'])
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
        return redirect(url_for('dashboard.profile'))
    
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
    return redirect(url_for('dashboard.profile'))

@dashboard_bp.route('/update-password', methods=['POST'])
@login_required
def update_password():
    current_user = g.current_user

    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')

    if  not check_password_hash(current_user.password_hash, current_password):
        flash('Incorrect password. Please try again.', 'password_error')
        return redirect(url_for('dashboard.profile', modal='password'))

    if new_password != confirm_password:
        flash('Passwords do not match. Please try again.', 'password_error')
        return redirect(url_for('dashboard.profile', modal='password'))

    hashed_password = generate_password_hash(new_password, method='pbkdf2:sha256')
    current_user.password_hash = hashed_password

    db.session.commit()
    flash('Password updated successfully!', 'profile_success')
    return redirect(url_for('dashboard.profile'))

@dashboard_bp.route('/delete-document/<int:doc_id>', methods=['POST'])
@login_required
def delete_document(doc_id):
    current_user = g.current_user 

    doc = Document.query.filter_by(id=doc_id, user_id=current_user.id).first()

    if doc:
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], doc.filename)
        if os.path.exists(file_path):
            os.remove(file_path)

        db.session.delete(doc)
        db.session.commit()
        flash("Project deleted successfully.", "info")
    else:
        flash("Document not found or access denied.", "danger")

    return redirect(url_for('dashboard.dashboard'))