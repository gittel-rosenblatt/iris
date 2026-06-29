from flask import Flask, render_template, request, redirect, url_of

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route('/our-story')
def story():
    return render_template('story.html') 
    
@app.route('/terms')
def terms():
    return render_template('terms.html') 

@app.route('/privacy')
def privacy():
    return render_template('privacy.html') 

@app.route('/login')
def login():
    if request.method == 'POST':
        login_title = request.login.get('login_title')
        login_description = request.login.get('login_description')
        
        print(f"New Form Created: {login_title} - {login_description}")
        
        return redirect('/dashboard')
        
    return render_template('workspace.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html') 
    
@app.route('/workspace')
def workspace():
    return render_template('workspace.html') 

@app.route('/profile')
def profile():
    return render_template('profile.html') 

if __name__ == "__main__":
    app.run(debug=True)