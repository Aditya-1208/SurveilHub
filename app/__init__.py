from flask import Flask, render_template, jsonify, request, redirect, url_for, flash
from flask_mail import Mail, Message  
from dotenv import load_dotenv
load_dotenv('.env')
import os
from config import Config
from flask_migrate import Migrate
from app.extensions import db
from app.models.camera import Camera
from werkzeug.utils import secure_filename
from app.emailFunction import send_email_helper

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
    app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_USERNAME')
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

    @app.route('/send-email', methods=['GET', 'POST'])
    def send_email():
        if request.method == 'POST':
            recipient = request.form.get('recipient')
            subject = request.form.get('subject')
            msg_body = request.form.get('msg_body')
            image_file = request.files.get('image')

            if image_file:
                # Read image file content
                image_filename = secure_filename(image_file.filename)
                image_content = image_file.read()
                image_attachment = (image_filename, image_file.content_type, image_content)
            else:
                image_attachment = None

            # Call send_email function
            send_email_helper(recipient, subject, msg_body, image=image_attachment)

            return "Email sent successfully!"
        else:
            return render_template('sending_email.html')
    

    @app.route('/index')
    def index():
        return render_template('index.html')
    
    return app

if __name__ == '__main__':
    app.run(debug=True)
