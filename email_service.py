from flask_mail import Message
from extension import mail
import traceback

def send_verification_email(email, fullname, verification_link):
    try:
        msg = Message(
            subject="Verify your Email",
            recipients=[email]
        )

        msg.body = f"""
            Hello {fullname},
            
            Thank you for registering.
            
            Click the link below to verify your email.
            
            {verification_link}
            """

        mail.send(msg)

    except Exception:
        traceback.print_exc()
        raise