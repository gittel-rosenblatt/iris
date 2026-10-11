import os

from datetime import timedelta, timezone
from dotenv import load_dotenv
from extensions import db, mail
from flask import Flask, g
from models import User, Document, login_required
from routes.main import main_bp
from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.projects import projects_bp

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=6)
app.config['SESSION_REFRESH_EACH_REQUEST'] = True

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///iris.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['MAIL_SERVER'] = 'sandbox.smtp.mailtrap.io'
app.config['MAIL_PORT'] = 2525
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'

db.init_app(app)
mail.init_app(app)

with app.app_context():
    db.create_all()

@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response

@app.context_processor
def inject_user():
    return dict(current_user=getattr(g, 'current_user', None))

@app.template_filter('isoformat_utc')
def isoformat_utc(dt):
    if not dt:
        return ""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.isoformat()

app.register_blueprint(main_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(projects_bp)

if __name__ == '__main__':
    app.run(debug=True)