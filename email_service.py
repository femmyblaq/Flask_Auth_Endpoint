from flask_mail import Message
from extension import mail

def send_verification_email(email, fullname, verification_link):
    msg = Message(
        subject="Verify your Email",
        recipients=[email]
    )
    msg.body = f"""
    Hello {fullname},

    Thank you for registering.

    Click the link below to verify your email.

    {verification_link}

    If you didn't register, please ignore this email.

    Regards,
    Your Team
    """

    mail.send(msg)