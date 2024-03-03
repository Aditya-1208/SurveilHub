import cv2
import imutils
import numpy as np
import time
import threading
import re
import pytesseract
import queue
from ultralytics import YOLO
from helper import *
from PIL import Image
from flask import Flask, request, jsonify, render_template, Response
pytesseract.pytesseract.tesseract_cmd = r'C:\Users\Prasanna P M\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'
VIDEO_PATH = "http://localhost:8080"

app = Flask(__name__)


FRAME_WIDTH = 400
FRAME_QUEUE_SIZE = 10
frame_queue = queue.Queue(maxsize=FRAME_QUEUE_SIZE)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video')
def video():
    return Response(video_stream_gen(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/draw_line')
def draw_line():
  return render_template('sampleImage.html')

@app.route('/save_coordinates', methods=['POST'])
def save_coordinates():
  # Access data from the POST request
  data = request.get_json()  # Alternatively, you could use request.form
  start_x = data.get('startX')
  start_y = data.get('startY')
  end_x = data.get('endX')
  end_y = data.get('endY')

  # Process the coordinates as needed (e.g., store in database, log to file, etc.)
  print('Start coordinates:', start_x, start_y)
  print('End coordinates:', end_x, end_y)

  return jsonify({'message': 'Coordinates received successfully'}), 201  # HTTP status code for created resource


def video_stream_gen():
    vid = cv2.VideoCapture(VIDEO_PATH)
    if not vid.isOpened():
        raise RuntimeError("Error opening video file")

    ml_model = YOLO(r"C:\Users\Prasanna P M\EC498_Major_Project\SurveilHub\app\best.pt")

    line_points = [(10, 400), (2000, 550)]  
    classes_to_count = [0, 1, 2, 3, 4, 5, 6] 
    w, h, fps = (int(vid.get(x)) for x in (cv2.CAP_PROP_FRAME_WIDTH, cv2.CAP_PROP_FRAME_HEIGHT, cv2.CAP_PROP_FPS))
    counter = ObjectCounter()
    counter.set_args(view_img=True, reg_pts=line_points, classes_names=ml_model.names, draw_tracks=True)
    video_writer = cv2.VideoWriter("counting_output.mp4",
                            cv2.VideoWriter_fourcc(*'mp4v'),
                        fps,
                        (w, h))


    try:
        def frame_processor():
            while True:
                ret, frame = vid.read()
                if not ret:
                    break

                try:
                    frame_queue.put(frame, block=False)
                except queue.Full:
                    pass

        frame_processor_thread = threading.Thread(target=frame_processor)
        frame_processor_thread.start()

        while True:
            frame = frame_queue.get()

            tracks = ml_model.track(frame, persist=True, show=False, classes=classes_to_count)

            frame = counter.start_counting(frame, tracks)
            video_writer.write(frame)


            image = frame[35:89, 1431:1855]
            retval, img = cv2.threshold(image, 225, 255, cv2.THRESH_BINARY)
            img = cv2.GaussianBlur(img, (11, 11), 0)
            img = cv2.medianBlur(img, 9)
            pil_image = Image.fromarray(img)
            text = pytesseract.image_to_string(pil_image, config=r'--psm 7 --oem 3 -l eng -c tessedit_char_whitelist=0123456789')
            print(text)


            _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
            frame_bytes = buffer.tobytes()

            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        
    except Exception as e:
        print(f"Error in video thread: {e}")
    finally:
        vid.release()


if __name__ == '__main__':
  app.run(debug=True)