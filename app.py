from flask import Flask, render_template, request, redirect, url_for

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

@app.route('/login')
def login():
    return render_template('login.html') 

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html') 
    
@app.route('/workspace')
def workspace():
    return render_template('workspace.html') 

@app.route('/profile')
def profile():
    return render_template('profile.html') 

@app.route("/forgot-password")
def forgot_password():
    return render_template("forgot-password.html") 

if __name__ == "__main__":
    app.run(debug=True)