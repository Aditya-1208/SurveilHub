from flask import Flask, render_template, jsonify, request, redirect, url_for, send_from_directory, Response
from dotenv import load_dotenv
load_dotenv('.env')
from config import Config
from flask_migrate import Migrate
from app.extensions import db
from app.models.camera import Camera
from app.models.object_detection import ObjectDetection
# from utils.predictive_models.yolo_model.yolo_model import YOLOModel
# from utils.surveillance_applications.object_counter.counter_application import CounterApplication
import subprocess
from PIL import Image
import pytesseract
import cv2
import os

camera_processes = {}
line_points=[]


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
        consumer_path = os.path.join(current_dir, 'consumer.py')

        # Start streaming subprocess for the given URL
        cmd = [python_exe, producer_path, '--url', url] # Modify the command to include the URL parameter
        return subprocess.Popen(cmd)
    
    def run_model_inference():
        current_dir = os.path.dirname(os.path.realpath(__file__))
        venv_path = os.path.abspath(os.path.join(current_dir, '..', '.venv', 'Scripts'))
        python_exe = os.path.join(venv_path, 'python.exe')
        inference_path = os.path.join(current_dir,'model_inference.py',)
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
    
    @app.route('/inference_output')
    def inference_output():
        return render_template('inference_output.html')

    @app.route('/draw_line/<file_name>')
    def draw_line(file_name):
        return render_template('sampleImage.html', file_name= file_name)

    @app.route('/upload_image')
    def upload_f():
        return render_template('upload.html')
    
    @app.route('/display_image', methods = ['GET', 'POST'])
    def upload_file():
        if request.method == 'POST':
            f = request.files['file']
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], f.filename))
            return redirect(url_for('display_image', filename=f.filename))
        
    @app.route('/display_image/<filename>')
    def display_image(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


    @app.route('/save_coordinates', methods=['POST'])
    def save_coordinates():
        data = request.get_json()
        print('Received coordinates:', data)
        line_points = [(point['x'], point['y']) for point in data]
        print(line_points)
        return jsonify({'message': 'Coordinates received successfully'}), 201
    
    # @app.route('/video')
    # def video():
    #     return Response(video_stream_gen(), mimetype='multipart/x-mixed-replace; boundary=frame')
    
    # def video_stream_gen():
        # vid = cv2.VideoCapture(VIDEO_PATH)
        # if not vid.isOpened():
        #     raise RuntimeError("Error opening video file")

        # ml_model = YOLOModel()
        # counter = CounterApplication(ml_model, line_points)


        # try:
        #     def frame_processor():
        #         while True:
        #             ret, frame = vid.read()
        #             if not ret:
        #                 continue

        #             try:
        #                 frame_queue.put(frame, block=False)
        #             except queue.Full:
        #                 pass

        #     frame_processor_thread = threading.Thread(target=frame_processor)
        #     frame_processor_thread.start()

        #     while True:
        #         frame = frame_queue.get()
        #         frame = counter.count(frame)
        #         # video_writer.write(frame)

        #         image = frame[35:89, 1431:1855]
        #         retval, img = cv2.threshold(image, 225, 255, cv2.THRESH_BINARY)
        #         img = cv2.GaussianBlur(img, (11, 11), 0)
        #         img = cv2.medianBlur(img, 9)
        #         pil_image = Image.fromarray(img)
        #         text = pytesseract.image_to_string(pil_image, config=r'--psm 7 --oem 3 -l eng -c tessedit_char_whitelist=0123456789')
        #         print(text)


        #         _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
        #         frame_bytes = buffer.tobytes()

        #         yield (b'--frame\r\n'
        #             b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            
        # except Exception as e:
        #     print(f"Error in video thread: {e}")
        # finally:
        #     vid.release()

    @app.route('/camera/<int:camera_id>')
    def view_camera(camera_id):
        # Fetch the camera from the database using the camera_id
        camera = Camera.query.get_or_404(camera_id)
        
        # Now, render the index.html page with the camera's details
        # You might need to adjust this depending on how index.html uses the camera's details
        return render_template('index.html', camera=camera)

    # @app.route('/index')
    # def index():
    #     return render_template('index.html')
    
    return app

if __name__ == '__main__':
    app.run()
