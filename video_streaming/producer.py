import os
import cv2
import argparse
from dotenv import load_dotenv
from kafka import KafkaProducer

load_dotenv('.env')

topic = "videostreaming"

def publish_video(url):
    """
    Publish video file specified in environment variable VIDEO_PATH to a specified Kafka topic.
    Kafka Server is expected to be running on the localhost. Not partitioned.
    """
    # Start up producer
    producer = KafkaProducer(bootstrap_servers='localhost:9092')

    # Open file
    video = cv2.VideoCapture(url)
    success, image = video.read()
    print('publishing video...')
    count = 0

    while video.isOpened():
        success, image = video.read()
        if not success:
            break

        frame = cv2.imencode('.jpg', image)
        if len(frame) <= 1:
            print("no data")
            continue

        frame_bytes = frame[1]
        count += 1
        if (count - 1) % int(os.getenv('FRAME_RATE')) == 0:
            producer.send(topic, bytearray(frame_bytes))
            print("Frame published to Kafka topic:", topic)


    video.release()
    print('publish complete')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--url', help='URL of the video file')
    args = parser.parse_args()

    url = args.url
    publish_video(url)

