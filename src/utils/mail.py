from flask import current_app as app
from flask_mail import Message

from extensions import mail


def send_email(mail_recipient, mail_subject, template):
    msg = Message(
        subject=mail_subject,
        recipients=[mail_recipient],
        html=template,
        sender=app.config['MAIL_DEFAULT_SENDER'],
        extra_headers={'X-Priority': '2'}
    )
    mail.send(message=msg)