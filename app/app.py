import os
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
from flask import Flask, request, jsonify, render_template, Response, send_from_directory, redirect, url_for
pytesseract.pytesseract.tesseract_cmd = r'C:\Users\Prasanna P M\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'
VIDEO_PATH = "http://localhost:8080"

app = Flask(__name__)


app.config['UPLOAD_FOLDER'] = 'C:\\Users\\Prasanna P M\\EC498_Major_Project\\SurveilHub\\app\\Images'

@app.route('/')
def index():
    return render_template('index.html')


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

    ml_model = YOLOModel
    counter = CounterApplication(ml_model)
    # w, h, fps = (int(vid.get(x)) for x in (cv2.CAP_PROP_FRAME_WIDTH, cv2.CAP_PROP_FRAME_HEIGHT, cv2.CAP_PROP_FPS))
    # video_writer = cv2.VideoWriter("counting_output.mp4",
    #                         cv2.VideoWriter_fourcc(*'mp4v'),
    #                     fps,
    #                     (w, h))


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
            frame = counter.count(frame)
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