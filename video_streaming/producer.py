import os
import sys
import time
import cv2
from dotenv import load_dotenv
from kafka import KafkaProducer

load_dotenv('.env')

topic = "videostreaming"

def publish_video(video_file):
    """
    Publish given video file to a specified Kafka topic. 
    Kafka Server is expected to be running on the localhost. Not partitioned.
    
    :param video_file: path to video file <string>
    """
    # Start up producer
    producer = KafkaProducer(bootstrap_servers='localhost:9092')

    # Open file
    video = cv2.VideoCapture(video_file)
    success, image = video.read()
    print('publishing video...')
    count = 0

    while(video.isOpened()):
        frame = cv2.imencode('.jpg', image)
        if len(frame) <= 1:
            print("no data")
            continue

        frame_bytes = frame[1]
        success, image = video.read()
        count += 1
        if (count - 1) % int(os.getenv('FRAME_RATE')) == 0:
            producer.send(topic, bytearray(frame_bytes))
            print("Frame published to Kafka topic:", topic)  # Print statement to indicate frame publication

    video.release()
    print('publish complete')


if __name__ == '__main__':
    """
    Producer will publish to Kafka Server a video file given as a system arg. 
    Otherwise it will default by streaming webcam feed.
    """
    
    video_path = r"C:\Users\Prasanna P M\EC498_Major_Project\SurveilHub\video_streaming\clip.mp4"
    publish_video(video_path)
