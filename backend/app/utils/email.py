import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from ..core.config import settings

def send_email(to_email: str, subject: str, body: str):
    """Send email using SMTP."""
    try:
        msg = MIMEMultipart()
        msg['From'] = settings.SMTP_USERNAME
        msg['To'] = to_email
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'html'))

        server = smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT)
        server.starttls()
        server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
        text = msg.as_string()
        server.sendmail(settings.SMTP_USERNAME, to_email, text)
        server.quit()
        return True
    except Exception as e:
        print(f"Email sending failed: {e}")
        return False

def send_password_reset_email(email: str, reset_token: str):
    """Send password reset email."""
    subject = "Password Reset Request"
    body = f"""
    <h2>Password Reset</h2>
    <p>You requested a password reset. Click the link below to reset your password:</p>
    <a href="{settings.FRONTEND_URL}/reset-password?token={reset_token}">Reset Password</a>
    <p>This link will expire in 30 minutes.</p>
    """
    return send_email(email, subject, body)

def send_welcome_email(email: str, name: str):
    """Send welcome email to new users."""
    subject = "Welcome to D.O.C!"
    body = f"""
    <h2>Welcome {name}!</h2>
    <p>Thank you for joining D.O.C. Your account has been created successfully.</p>
    <p>You can now start using our medication management features.</p>
    """
    return send_email(email, subject, body)
