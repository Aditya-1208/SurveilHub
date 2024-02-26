from flask import Flask, render_template, jsonify, request, redirect, url_for
from dotenv import load_dotenv
load_dotenv('.env')
from config import Config
from flask_migrate import Migrate
from app.extensions import db
from app.models.camera import Camera
from app.models.object_detection import ObjectDetection

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

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
            return redirect(url_for('get_cameras'))
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

    @app.route('/index')
    def index():
        return render_template('index.html')
    
    return app

if __name__ == '__main__':
    app.run()
