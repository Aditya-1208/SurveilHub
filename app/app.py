import cv2
import imutils
from flask import Flask, render_template, Response
import numpy as np
import time
import threading
import re
import pytesseract
import queue
from ultralytics import YOLO
from helper import *

app = Flask(__name__)
pytesseract.pytesseract.tesseract_cmd = r'C:\Users\Prasanna P M\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'
# Set video file path (replace with your actual path)
VIDEO_PATH = "http://localhost:8080"

# Frame processing and display thread settings
FRAME_WIDTH = 400
FRAME_QUEUE_SIZE = 10
frame_queue = queue.Queue(maxsize=FRAME_QUEUE_SIZE)



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


            roi = frame[30:80, 1350:1800]  # Adjust ROI coordinates if needed
            gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
            blur = cv2.GaussianBlur(gray, (5, 5), 0)
            _, thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            kernel = np.ones((1, 1), np.uint8)
            img_dilation = cv2.dilate(thresh, kernel, iterations=1)
            img_erosion = cv2.erode(img_dilation, kernel, iterations=1)
            text = pytesseract.image_to_string(img_erosion)
            # Extract timestamp and handle potential None type
            match = re.search(r'\d{2}:\d{2}:\d{2}', text)
            time_str = match.group() if match else None  # Use a default value if no match

            print("Timestamp :", time_str)


            _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
            frame_bytes = buffer.tobytes()

            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        
    except Exception as e:
        print(f"Error in video thread: {e}")
    finally:
        vid.release()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video')
def video():
    return Response(video_stream_gen(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(debug=True)