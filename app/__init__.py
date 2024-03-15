from flask import Flask, render_template, jsonify, request, redirect, url_for, flash
from flask_mail import Mail, Message  
from dotenv import load_dotenv
load_dotenv('.env')
import os
from config import Config
from flask_migrate import Migrate
from app.extensions import db
from app.models.camera import Camera
from app.models.object_detection import ObjectDetection
#from sending_mail import send_mail_with_image
from main_mail import send_email
#from test import send_email

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Configure Flask-Mail with your email server details
    app.config['MAIL_SERVER']= 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 465
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
    app.config['MAIL_USE_TLS'] = False
    app.config['MAIL_USE_SSL'] = True
    mail = Mail(app)

    # Initialize Flask-Mail extension
    mail = Mail(app)

    db.init_app(app)
    migrate = Migrate(app, db)

    @app.route('/')
    def home():
        cameras = Camera.query.all()
        cameras_data = [{'id': camera.id, 'name': camera.name, 'connection_url': camera.connection_url} for camera in cameras]
        return render_template('main_dashboard.html',cameras=cameras_data)

    # Route to create a new camera
    @app.route('/cameras', methods=['GET','POST'])
    def create_camera():
        if request.method == 'POST':
            name = request.form['name']
            connection_url = request.form['connection_url']
            new_camera = Camera(name=name, connection_url=connection_url)
            db.session.add(new_camera)
            db.session.commit()
            return redirect(url_for('home'))
        return render_template('create_camera.html')
    
    @app.route('/create-camera', methods=['GET'])
    def create_camera_page():
        return render_template('create_camera.html')
    
    @app.route('/create-camera', methods=['POST'])
    def create_camera_post():
        name = request.form['name']
        connection_url = request.form['connection_url']
        
        # Create a new camera object and add it to the database
        new_camera = Camera(name=name, connection_url=connection_url)
        db.session.add(new_camera)
        db.session.commit()
        
        # Redirect the user back to the main dashboard page
        return redirect(url_for('get_cameras'))

    @app.route('/camera/<int:camera_id>')
    def view_camera(camera_id):
        # Fetch the camera from the database using the camera_id
        camera = Camera.query.get_or_404(camera_id)
        
        # Now, render the index.html page with the camera's details
        # You might need to adjust this depending on how index.html uses the camera's details
        return render_template('index.html', camera=camera)

    @app.route('/send-email', methods=['GET','POST'])
    def send_email_route():
        if request.method == 'POST':
            recipients = [request.form['recipient']]
            subject = request.form['subject']
            body = request.form['body']

            if 'image' not in request.files:
                flash('No image provided', 'error')
                return render_template('sending_email.html')

            image_file = request.files['image']
            if image_file.filename == '':
                flash('No image filename provided', 'error')
                return render_template('sending_email.html')

            image_filename = image_file.filename
            image_mime_type = image_file.mimetype

            attachments = [{'path': image_file, 'filename': image_filename, 'mime_type': image_mime_type}]

            try:
                send_email(mail, recipients, subject, body, attachments)
                flash('Email sent successfully', 'success')
            except Exception as e:
                flash('Failed to send email: ' + str(e), 'error')

            return render_template('sending_email.html')
    #    if request.method == 'POST':
    #         recipients = request.form.getlist('recipients')
    #         subject = request.form['subject']
    #         body = request.form['body']
    #         attachments = []

    #         # Handle file upload
    #         if 'attachment' in request.files:
    #             attachment = request.files['attachment']
    #             if attachment.filename != '':
    #                 attachments.append({
    #                     'path': attachment,
    #                     'filename': attachment.filename,
    #                     'mime_type': attachment.content_type
    #                 })

    #         # Send email
    #         try:
    #             send_email(recipients, subject, body, attachments)
    #             flash('Email sent successfully', 'success')
    #         except Exception as e:
    #             flash('Failed to send email: ' + str(e), 'error')

    #         return render_template('sending_email.html')

        # recipient = request.form['recipient']
        # subject = request.form['subject']
        # body = request.form['body']

        # if 'image' not in request.files:
        #     return "No image provided", 400

        # image_file = request.files['image']
        # image_filename = image_file.filename
        # if not image_filename:
        #     return "No image filename provided", 400

        # image_data = image_file.read()
        # image_type = 'image/png'  # Assuming the image is always a PNG file

        # msg = Message(subject=subject, recipients=[recipient])
        # msg.body = body
        # msg.attach(image_filename, image_type, image_data)

        # try:
        #     mail.send(msg)
        #     return "Message sent successfully"
        # except Exception as e:
        #     return f"Failed to send message: {str(e)}", 500

    #     if request.method == 'POST':
    #         recipient = request.form['recipient']
    #         subject = request.form['subject']
    #         body = request.form['body']
    #         image = request.files['image']

    #         if image.filename == '':
    #             flash('No selected image')
    #             return redirect(request.url)

    #         if recipient and subject and body and image:
    #             try:
    #                 send_mail_with_image(recipient, subject, body, image)
    #                 flash('Email sent successfully')
    #             except Exception as e:
    #                 flash('Failed to send email: ' + str(e))
    #         else:
    #             flash('All form fields are required')

    #     return render_template('sending_email.html')

# def send_mail_with_image(recipient, subject, body, image):
#     image_data = image.read()
#     image_type = 'image/png'  # Assuming the image is always a PNG file

#     msg = Message(subject=subject, recipients=[recipient])
#     msg.body = body
#     msg.attach(image.filename, image_type, image_data)

#     mail.send(msg)

#     @app.route('/index')
#     def index():
#         return render_template('index.html')
    
    return app

if __name__ == '__main__':
    app.run(debug=True)
