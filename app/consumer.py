import cv2
from kafka import KafkaConsumer
import numpy as np

topic = "videostreaming"


def consume_video():
    """
    Consume video frames from a specified Kafka topic and display them.
    Kafka Server is expected to be running on the localhost.
    """
    consumer = KafkaConsumer(
    topic, 
    bootstrap_servers=['localhost:9092'])

    for message in consumer:
        frame_bytes = bytearray(message.value)
        frame_np = np.frombuffer(frame_bytes, dtype=np.uint8)
        frame = cv2.imdecode(frame_np, cv2.IMREAD_COLOR)
        cv2.imshow('Video', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()

if __name__ == 'main':
    """
    Consumer will consume frames from Kafka topic and display them.
    """
    consume_video()