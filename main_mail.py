from flask_mail import Message

def send_email(mail, recipients, subject, body, attachments=None):
    msg = Message(subject=subject, recipients=recipients)
    msg.body = body

    if attachments:
        for attachment in attachments:
            with mail.open_resource(attachment['path']) as f:
                msg.attach(attachment['filename'], attachment['mime_type'], f.read())

    mail.send(msg)
