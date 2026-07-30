
# from extension import mail
from brevo import Brevo
from config import Config
from flask import current_app
from brevo.transactional_emails import (SendTransacEmailRequestSender, 
                                        SendTransacEmailRequestToItem)

def send_verification_email(email, subject, html):
    client = Brevo(
        api_key=current_app.config["BREVO_API_KEY"]
    )
    client.transactional_emails.send_transac_email(
        subject=subject,
        html_content=html,
        sender=SendTransacEmailRequestSender(
            name=current_app.config["MAIL_FROM_TITLE"],
            email=current_app.config["MAIL_FROM"]
        ),
        to=[
            SendTransacEmailRequestToItem(
                email=email
            )
        ]
    )    
        

    