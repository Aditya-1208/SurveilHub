from flask import Flask, render_template, jsonify, request, redirect, url_for, send_from_directory, Response,flash
from flask_mail import Mail
from dotenv import load_dotenv
load_dotenv('.env')
import os
from config import Config
from flask_migrate import Migrate
from app.extensions import db
from app.models.camera import Camera
from werkzeug.utils import secure_filename
from app.utils.emailFunction import send_email_helper
from app.models.object_detection import ObjectDetection
# from utils.predictive_models.yolo_model.yolo_model import YOLOModel
# from utils.surveillance_applications.object_counter.counter_application import CounterApplication
import subprocess
from PIL import Image
import pytesseract
import cv2
import ast

camera_processes = {}
line_points=[]



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

    # app.config['UPLOAD_FOLDER'] = 'C:\\Users\\Prasanna P M\\EC498_Major_Project\\SurveilHub\\app\\Images'


    db.init_app(app)
    migrate = Migrate(app, db)

    @app.route('/')
    def home():
        cameras = Camera.query.all()
        return render_template('main_dashboard.html',cameras=cameras)

    # Route to create a new camera
    @app.route('/cameras', methods=['GET'])
    def create_camera():
        return render_template('create_camera.html')
    
    @app.route('/create-camera', methods=['GET'])
    def create_camera_page():
        return render_template('create_camera.html')
    
    def start_streaming(url = "http://localhost:9000/"):
    # Path to Python executable in the virtual environment
        current_dir = os.path.dirname(os.path.realpath(__file__))
        venv_path = os.path.abspath(os.path.join(current_dir, '..', '.venv', 'Scripts'))
        python_exe = os.path.join(venv_path, 'python.exe')
        producer_path = os.path.join(current_dir, 'producer.py')
        cmd = [python_exe, producer_path, '--url', url] # Modify the command to include the URL parameter
        return subprocess.Popen(cmd)
    
    def run_model_inference(camera_id):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        venv_path = os.path.abspath(os.path.join(current_dir, '..', '.venv', 'Scripts'))
        python_exe = os.path.join(venv_path, 'python.exe')
        inference_path = os.path.join(current_dir,'model_inference.py',)
        camera = Camera.query.get_or_404(camera_id)
        print("Regions : ",camera.get_regions_innermost_tuple_string())
        all_points_array = ast.literal_eval(camera.get_regions_innermost_tuple_string())
        line_points_arrays = []
        for sub_array in all_points_array:
            if len(sub_array) == 2:
                line_points_arrays.append(sub_array)

        for line_points_array in line_points_arrays:
            all_points_array.remove(line_points_array)
            
        # region_points = [[(680, 257), (986, 125), (1174, 189), (930, 290)], [(602, 530), (450, 434), (626, 308), (1106, 415)]]
        region_points = all_points_array
        line_points = line_points_arrays[0]
        # line_points = [(10, 700), (2000, 1100)]
        recipients = camera.get_alert_emails()
        cmd = [python_exe, inference_path, '--camera_id', str(camera_id), '--region_points', str(region_points), '--line_points', str(line_points), '--recipients', str(recipients)] # Modify the command to include the URL parameter
        return subprocess.Popen(cmd)
    
    @app.route('/create-camera', methods=['POST'])
    def create_camera_post():
        name = request.form['name']
        connection_url = request.form['connection_url']
        description = request.form['description']
        new_camera = Camera(name=name, connection_url=connection_url, description=description)
        db.session.add(new_camera)
        db.session.commit()
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
        return render_template('camera/settings.html', camera=camera)

    @app.route('/update_camera/<int:camera_id>', methods=['POST'])
    def update_camera(camera_id):
        camera = Camera.query.get_or_404(camera_id)
        camera.name = request.form['name']
        camera.connection_url = request.form['connection_url']
        camera.description = request.form['description']
        camera.state = bool(request.form.get('state'))
        camera.set_regions(request.form.get('regions'))
        camera.set_region_colors(request.form.get('region_colors'))
        camera.alert_emails = request.form.get('alert_emails')
        db.session.commit()
        return redirect(url_for('view_camera', camera_id=camera.id))

    @app.route('/camera/<int:camera_id>/intrusions', methods=['GET'])
    def view_intrusions(camera_id):
        camera = Camera.query.get_or_404(camera_id)
        return render_template('camera/intrusions.html', camera=camera)
        
    @app.route('/camera/<int:camera_id>/object_detections', methods=['GET'])
    def view_object_detections(camera_id):
        camera = Camera.query.get_or_404(camera_id)
        object_detections = ObjectDetection.query.filter_by(camera_id=camera_id).all()

        class_counts = {}
        for detection in object_detections:
            predicted_class = detection.predicted_class
            if predicted_class in class_counts:
                class_counts[predicted_class] += 1
            else:
                class_counts[predicted_class] = 1
        
        return render_template('camera/object_detections.html', camera=camera, object_detections=object_detections, class_counts=class_counts)

    @app.route('/camera/<int:camera_id>/traffic_insights', methods=['GET'])
    def view_traffic_insights(camera_id):
        camera = Camera.query.get_or_404(camera_id)
        return render_template('camera/traffic_insights.html', camera=camera)
    

    @app.route('/camera/<int:camera_id>/fetch_frame', methods=['GET'])
    def fetch_camera_frame(camera_id):
        camera = Camera.query.get_or_404(camera_id)
        camera.capture_frame()
        return redirect(url_for('view_camera', camera_id=camera.id))

    @app.route('/camera/<int:camera_id>/start_stream', methods=['GET'])
    def start_stream(camera_id):
        camera = Camera.query.get_or_404(camera_id)
        if camera.id not in camera_processes:
            streaming_process = start_streaming(camera.connection_url)
            inference_process = run_model_inference(camera_id)
            camera_processes[camera.id] = (streaming_process,inference_process)
            camera.state = True
            db.session.commit()
        return redirect(url_for('view_camera', camera_id=camera.id))


    @app.route('/send-email', methods=['GET', 'POST'])
    def send_email():
        if request.method == 'POST':
            recipients = request.json.get('recipients')
            subject = request.json.get('subject')
            msg_body = request.json.get('msg_body')
            image_path = request.json.get('image')

            image_attachment = None
            if image_path:
                # Assuming the image path is provided
                with open(image_path, 'rb') as image_file:
                    image_content = image_file.read()
                    image_attachment = ('image.jpg', 'image/jpeg', image_content)

            # Call send_email function
            send_email_helper(recipients, subject, msg_body, image=image_attachment)

            return "Email sent successfully!"
        else:
            return render_template('sending_email.html')
    

    @app.route('/camera/<int:camera_id>/object_detection', methods=['POST'])
    def store_object_detection(camera_id):
        data = request.json
        predicted_class = data.get('predicted_class')
        timestamp_str = data.get('timestamp')
        additional_info = data.get('additional_info')

        detection = ObjectDetection(
            camera_id=camera_id,
            predicted_class=predicted_class,
            timestamp=timestamp,
            additional_info=additional_info
        )

        # Add and commit to database
        db.session.add(detection)
        db.session.commit()

        return jsonify({'message': 'Object detection record stored successfully'}), 201

    @app.route('/index')
    def index():
        return render_template('index.html')

    # @app.route('/index')
    # def index():
    #     return render_template('index.html')

    
    return app

if __name__ == '__main__':
    app.run(debug=True)
