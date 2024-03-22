from kafka import KafkaConsumer
from PIL import Image
import pytesseract
import cv2
import os
import threading
import numpy as np
import argparse
import json
import queue
import sys
import ast
from datetime import datetime
from dotenv import load_dotenv
load_dotenv('.env')
from utils.predictive_models.yolo_model.yolo_model import YOLOModel
from utils.surveillance_applications.object_counter.counter_application import CounterApplication
from utils.surveillance_applications.intrusion.intrusion_application import IntrusionApplication
import uuid
import requests
import re

# pytesseract.pytesseract.tesseract_cmd = r'C:\Users\Prasanna P M\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'
# line_points=[(10, 400), (2000, 550)]


def timestampExtraction(frame):
    image = frame[35:89, 1431:1855]
    retval, img = cv2.threshold(image, 225, 255, cv2.THRESH_BINARY)
    img = cv2.GaussianBlur(img, (11, 11), 0)
    img = cv2.medianBlur(img, 9)
    pil_image = Image.fromarray(img)
    text = pytesseract.image_to_string(pil_image, config=r'--psm 7 --oem 3 -l eng -c tessedit_char_whitelist=0123456789')
    return text

def consume_kafka_stream(camera_id, region_points, line_points, emails):
    # Set your Kafka broker address
    bootstrap_servers = 'localhost:9092'
    topic = 'videostreaming'

    consumer = KafkaConsumer(topic,
                             bootstrap_servers=bootstrap_servers)

    print("connected to kafka broker")
    ml_model = YOLOModel()
    lineCounter = CounterApplication(ml_model, line_points)
    intrusionDetection = IntrusionApplication(ml_model, region_points)

    try:
        for message in consumer:
            frame_bytes = bytearray(message.value)
            frame_np = np.frombuffer(frame_bytes, dtype=np.uint8)
            frame = cv2.imdecode(frame_np, cv2.IMREAD_COLOR)

            # Perform inference on the frame
            object_class_name = lineCounter.count(frame)
            intrusion_frame = intrusionDetection.count(frame)
            if intrusion_frame is not None:
                region_text = timestampExtraction(intrusion_frame)
                print(region_text)
                unique_filename = str(uuid.uuid4())
                save_path = os.path.join(os.path.dirname(__file__),'static', 'camera','intrusions', f'{unique_filename}.jpg')
                cv2.imwrite(save_path, intrusion_frame)
                data = {
                    "recipients": emails,
                    "subject": "Instrusion detected",
                    "msg_body": "An intrusion has been detected in your defined region!",
                    "image": save_path
                }
                # send_email_helper("An intrusion has been detected in your defined region!",image=save_path)
                requests.post("http://localhost:5000/send-email", json = data)


    except KeyboardInterrupt:
        # Handle keyboard interrupt (Ctrl+C) gracefully
        print("Quitting gracefully")
        pass

    finally:
        # Close the Kafka consumer when done
        consumer.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process video stream with object detection.')
    parser.add_argument('--camera_id', type=int, help='Camera ID', required=True)
    parser.add_argument('--region_points', type=str, help='Region points as a list of tuples', required=True)
    parser.add_argument('--line_points', type=str, help='Line points as a tuple', required=True)
    parser.add_argument('--recipients', type=str, help='Array of recipient email addresses as a JSON-formatted string', required=True)
    args = parser.parse_args()

    camera_id = args.camera_id
    region_points = eval(args.region_points)
    line_points = eval(args.line_points)
    emails = ast.literal_eval(args.recipients)

    print("Line points", line_points)
    consume_kafka_stream(camera_id, region_points, line_points, emails)
