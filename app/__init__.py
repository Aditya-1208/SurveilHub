from flask import Flask, render_template, jsonify, request, redirect, url_for
from dotenv import load_dotenv
load_dotenv('.env')
from config import Config
from flask_migrate import Migrate
from app.extensions import db
from app.models.camera import Camera
from app.models.object_detection import ObjectDetection
import subprocess
import os

camera_processes = {}


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
            return redirect(url_for('home'))
        return render_template('create_camera.html')
    
    @app.route('/create-camera', methods=['GET'])
    def create_camera_page():
        return render_template('create_camera.html')
    
    def start_streaming(url):
    # Path to Python executable in the virtual environment
        current_dir = os.path.dirname(os.path.realpath(__file__))
        venv_path = os.path.abspath(os.path.join(current_dir, '..', '.venv', 'Scripts'))
        python_exe = os.path.join(venv_path, 'python.exe')
        producer_path = os.path.join(current_dir, 'producer.py')

        # Start streaming subprocess for the given URL
        cmd = [python_exe, producer_path, '--url', url] # Modify the command to include the URL parameter
        return subprocess.Popen(cmd)
    
    def run_model_inference():
        current_dir = os.path.dirname(os.path.realpath(__file__))
        venv_path = os.path.abspath(os.path.join(current_dir, '..', '.venv', 'Scripts'))
        python_exe = os.path.join(venv_path, 'python.exe')
        inference_path = os.path.join(current_dir,'..','model_inference','main.py')
        cmd = [python_exe, inference_path] # Modify the command to include the URL parameter
        return subprocess.Popen(cmd)
    
    @app.route('/create-camera', methods=['POST'])
    def create_camera_post():
        name = request.form['name']
        connection_url = request.form['connection_url']
        
        # Create a new camera object and add it to the database
        new_camera = Camera(name=name, connection_url=connection_url)
        db.session.add(new_camera)
        db.session.commit()

        streaming_process = start_streaming(connection_url)
        inference_process = run_model_inference()
        camera_processes[new_camera.id] = (streaming_process,inference_process)
        
        # Redirect the user back to the main dashboard page
        return redirect(url_for('home'))

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
