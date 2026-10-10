from datetime import datetime, timezone
from extensions import db, cipher
from flask import redirect, session, url_for, g
from functools import wraps

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

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('auth.login'))
        
        current_user = User.query.filter_by(username=session['user']).first()
        if not current_user:
            session.clear()
            return redirect(url_for('auth.login'))
            
        g.current_user = current_user
        return f(*args, **kwargs)
    return decorated_function