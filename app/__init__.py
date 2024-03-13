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
    def send_email():
        # if request.method == 'POST':
        #     # Get user input from the form
        #     subject = request.form['subject']
        #     recipient = request.form['recipient']
        #     message_body = request.form['message_body']

        #     # Create a Flask-Mail Message object
        #     msg = Message(subject, sender='your_email@example.com', recipients=[recipient])
        #     msg.body = message_body

        #     try:
        #         # Send the email
        #         mail.send(msg)
        #         return "Email sent successfully!"
        #     except Exception as e:
        #         return f"Error sending email: {str(e)}"
        msg = Message(subject='Hello from the other side!', sender=os.getenv('MAIL_USERNAME'), recipients=['aditya.agr.btp@gmail.com'])
        msg.body = "Hey Paul, sending you this email from my Flask app, lmk if it works"
        mail.send(msg)
        return "Message sent!"

    @app.route('/index')
    def index():
        return render_template('index.html')
    
    return app

if __name__ == '__main__':
    app.run(debug=True)
