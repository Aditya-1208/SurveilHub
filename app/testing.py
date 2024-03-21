from PIL import Image
import pytesseract
import cv2
import os
import threading
import numpy as np
import queue
from utils.predictive_models.yolo_model.yolo_model import YOLOModel
from utils.surveillance_applications.object_counter.counter_application import CounterApplication
from utils.surveillance_applications.intrusion.intrusion_application import IntrusionApplication
from flask import current_app
import uuid
import requests
import re
# VIDEO_PATH = r"C:\Users\Prasanna P M\EC498_Major_Project\clip.mp4"
FRAME_WIDTH = 400
FRAME_QUEUE_SIZE = 10
frame_queue = queue.Queue(maxsize=FRAME_QUEUE_SIZE)
# region_points=[[(680, 257), (986, 125), (1174, 189), (930, 290)],[(602, 530), (450, 434), (626, 308), (1106, 415)]]
region_points=[[(680, 257), (986, 125), (1174, 189), (930, 290)], [(602, 530), (450, 434), (626, 308), (1106, 415)]]
line_points = [(10, 700), (2000, 1100)]

def timestampExtraction(frame):
    image = frame[35:89, 1431:1855]
    retval, img = cv2.threshold(image, 225, 255, cv2.THRESH_BINARY)
    img = cv2.GaussianBlur(img, (11, 11), 0)
    img = cv2.medianBlur(img, 9)
    pil_image = Image.fromarray(img)
    text = pytesseract.image_to_string(pil_image, config=r'--psm 7 --oem 3 -l eng -c tessedit_char_whitelist=0123456789')
    return text

def video_stream_gen(url):
    vid = cv2.VideoCapture(url)
    ml_model = YOLOModel()
    lineCounter = CounterApplication(ml_model, line_points)
    intrusionDetection = IntrusionApplication(ml_model, region_points)
    try:
        def frame_processor():
            while True:
                ret, frame = vid.read()
                if not ret:
                    print("Error reading frame from video stream")
                    break
                try:
                    frame_queue.put(frame, block=False)
                except queue.Full:
                    pass
        frame_processor_thread = threading.Thread(target=frame_processor)
        frame_processor_thread.start()
        while True:
            frame = frame_queue.get()
            object_class_name = lineCounter.count(frame)
            intrusion_frame = intrusionDetection.count(frame)
            if intrusion_frame is not None:
                region_text = timestampExtraction(intrusion_frame)
                print(region_text)
                unique_filename = str(uuid.uuid4())
                save_path = os.path.join(os.path.dirname(__file__),'static', 'camera','intrusions', f'{unique_filename}.jpg')
                cv2.imwrite(save_path, intrusion_frame)
                data = {
                    "recipients": ["adityaagr012@gmail.com"],
                    "subject": "Instrusion detected",
                    "msg_body": "An intrusion has been detected in your defined region!",
                    "image": save_path
                }
                # send_email_helper("An intrusion has been detected in your defined region!",image=save_path)
                requests.post("http://localhost:5000/send-email", json = data)
            if object_class_name is not None:
                print(object_class_name)



    except KeyboardInterrupt:
        print("KeyboardInterrupt: Stopping video stream.")
    finally:
        vid.release()

if __name__ == '__main__':
    video_stream_gen("http://localhost:9000/")


