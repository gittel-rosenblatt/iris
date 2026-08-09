from flask import Flask, render_template, request, redirect, url_for

FAKE_USERS_DB = {
    'testuser': {
        'password': '1234',
        'question': 'pet',
        'answer': 'fluffy'
    }
}

app = Flask(__name__)

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

        if username == 'testuser' and password == '1234':
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html')
        # return redirect(url_for('dashboard'))
    
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
            'question': question,
            'answer': answer
        }

        print(f"Successfully registered new user: {username}")

        return redirect(url_for('profile'))

@app.route("/forgot-password")
def forgot_password():
    return render_template("forgot-password.html") 

@app.route("/reset-password")
def reset_password():
    return render_template("reset-question.html") 

@app.route('/dashboard', methods=['POST'])
def dashboard():
    return render_template('dashboard.html') 
    
@app.route('/workspace', methods=['POST'])
def workspace():
    return render_template('workspace.html') 

@app.route('/profile', methods=['POST'])
def profile():
    return render_template('profile.html') 

@app.route("/contact-and-faqs")
def contact():
    return render_template("contact.html") 

@app.route('/logout')
def logout():
    return redirect(url_for('login'))

@app.route('/update-profile', methods=['POST'])
def update_profile():
    return redirect(url_for('profile'))

@app.route('/update-password', methods=['POST'])
def update_password():
    return redirect(url_for('profile'))

if __name__ == "__main__":
    app.run(debug=True)