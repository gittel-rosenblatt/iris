from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os

FAKE_USERS_DB = {
    'testuser': {
        'password': '1234',
        'security_question': 'pet',
        'answer': 'fluffy'
    }
}

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///iris.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    security_question = db.Column(db.String(200), nullable=False)
    security_answer = db.Column(db.String(120), nullable=False)

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
        username = request.form.get('username')
        password = request.form.get('password')

        print(f"Attempted login with: {username} and password: {password}")

        if username in FAKE_USERS_DB and FAKE_USERS_DB[username]['password'] == password:
            session['user'] = username
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html')
    
    return render_template('login.html') 

@app.route('/signup', methods=['POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        question = request.form.get('security_question')
        answer = request.form.get('security-answer')

        if username in FAKE_USERS_DB:
            print(f"Signup failed: Username '{username}' already exists!")
            return render_template('login.html')

        FAKE_USERS_DB[username] = {
            'password': password,
            'security_question': question,
            'security_answer': answer
        }

        print(f"Successfully registered new user: {username}")

        session['user'] = username
        return redirect(url_for('profile'))

@app.route("/forgot-password", methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        username = request.form.get('username')

        if username in FAKE_USERS_DB:
            question = FAKE_USERS_DB[username].get('security_question')
            return render_template('reset-question.html', username=username, security_question=question)
        else:
            return render_template('forgot-password.html', error=True)

    return render_template("forgot-password.html") 

@app.route("/reset-password")
def reset_password():
    return render_template("reset-question.html") 

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))

    return render_template('dashboard.html') 
    
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
    return redirect(url_for('profile'))

@app.route('/update-password', methods=['POST'])
def update_password():
    return redirect(url_for('profile'))

if __name__ == "__main__":
    app.run(debug=True)