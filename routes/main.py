from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_mailman import EmailMultiAlternatives

main_bp = Blueprint('main', __name__)

@main_bp.route("/")
def home():
    return render_template("index.html")

@main_bp.route('/our-story')
def story():
    return render_template('story.html') 
    
@main_bp.route('/terms-of-service')
def terms():
    return render_template('terms.html') 

@main_bp.route('/privacy-policy')
def privacy():
    return render_template('privacy.html')

@main_bp.route("/contact-and-faqs")
def contact():
    return render_template("contact.html") 

@main_bp.route('/send-contact', methods=['POST'])
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

    return redirect(url_for('main.contact'))