from flask import current_app, render_template
from flask_mail import Message
from threading import Thread
from . import mail

def send_async_email(app, msg):
    """Send an email asynchronously."""
    with app.app_context():
        mail.send(msg)

def send_email(to, subject, template, **kwargs):
    """Send an email to the specified recipient.
    
    Args:
        to: Email address of the recipient
        subject: Email subject
        template: The template name (without .html)
        **kwargs: Variables to pass to the template
    """
    app = current_app._get_current_object()
    
    # If in development and no mail server is configured, print the email to console
    if app.config.get('MAIL_SUPPRESS_SEND') or app.testing:
        print(f"\n--- Email (not sent in {'test' if app.testing else 'development'} mode) ---")
        print(f"To: {to}")
        print(f"Subject: {subject}")
        print("Body:")
        print(render_template(f"{template}.txt", **kwargs))
        print("-----------------------\n")
        return
    
    # In production, send the actual email
    msg = Message(
        subject=app.config['MAIL_SUBJECT_PREFIX'] + ' ' + subject,
        sender=app.config['MAIL_SENDER'],
        recipients=[to]
    )
    
    # Render both HTML and plain text versions
    msg.body = render_template(f"{template}.txt", **kwargs)
    msg.html = render_template(f"{template}.html", **kwargs)
    
    # Send email asynchronously to avoid blocking the application
    Thread(target=send_async_email, args=(app, msg)).start()

def send_password_reset_email(user):
    """Send a password reset email to the user."""
    token = user.generate_reset_token()
    send_email(
        to=user.email,
        subject="Reset Your Password",
        template="auth/email/reset_password",
        user=user,
        token=token
    )

def send_email_confirmation(user):
    """Send an email confirmation email to the user."""
    token = user.generate_confirmation_token()
    send_email(
        to=user.email,
        subject="Confirm Your Email Address",
        template="auth/email/confirm",
        user=user,
        token=token
    )

def send_email_change_email(user, new_email):
    """Send an email to confirm an email address change."""
    token = user.generate_email_change_token(new_email)
    send_email(
        to=new_email,
        subject="Confirm Your New Email Address",
        template="auth/email/change_email",
        user=user,
        token=token,
        new_email=new_email
    )
