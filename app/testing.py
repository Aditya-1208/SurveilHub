from PIL import Image
import pytesseract
import cv2
import os
import threading
import numpy as np
import queue
from utils.predictive_models.yolo_model.yolo_model import YOLOModel
# from utils.surveillance_applications.object_counter.counter_application import CounterApplication
from utils.surveillance_applications.intrusion.intrusion_application import IntrusionApplication

import re
pytesseract.pytesseract.tesseract_cmd = r'C:\Users\Prasanna P M\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'

VIDEO_PATH = "http://localhost:8080/"
FRAME_WIDTH = 400
FRAME_QUEUE_SIZE = 10
frame_queue = queue.Queue(maxsize=FRAME_QUEUE_SIZE)
region_points=[(1072, 568), (441, 426), (984, 161), (1279, 283)]
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
    # lineCounter = CounterApplication(ml_model, line_points)
    intrusionDetection = IntrusionApplication(ml_model, region_points)
    try:
        def frame_processor():
            while True:
                ret, frame = vid.read()
                try:
                    frame_queue.put(frame, block=False)
                except queue.Full:
                    pass
        frame_processor_thread = threading.Thread(target=frame_processor)
        frame_processor_thread.start()
        while True:
            frame = frame_queue.get()
            # line_frame = lineCounter.count(frame)
            region_frame = intrusionDetection.count(frame)
            # line_text = timestampExtraction(line_frame)
            region_text = timestampExtraction(region_frame)
            print(region_text)



    except KeyboardInterrupt:
        print("KeyboardInterrupt: Stopping video stream.")
    finally:
        vid.release()

if __name__ == '__main__':
    video_stream_gen("http://localhost:8080/")
