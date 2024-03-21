from flask_mail import Message, Mail

def send_email_helper(recipients, subject, msg_body, image=None):
    """
    Helper function to send an email using Flask-Mail.
    
    Args:
        recipient (str): Email address of the recipient.
        subject (str): Subject of the email.
        msg_body (str): Body of the email.
        image (tuple, optional): Tuple containing filename, content type, and file content of image attachment.
    """
    mail = Mail()

    msg = Message(subject=subject, recipients=recipients)
    msg.body = msg_body

    if image:
        filename, content_type, file_content = image
        msg.attach(filename, content_type, file_content)

    try:
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False
