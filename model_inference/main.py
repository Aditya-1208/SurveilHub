import sys
import cv2
import PIL as Image
import pytesseract

sys.path.append("..")

from utils.predictive_models.yolo_model.yolo_model import YOLOModel
from utils.surveillance_applications.object_counter.counter_application import CounterApplication
from kafka import KafkaConsumer

line_points=[(10, 400), (2000, 550)]
ml_model = YOLOModel()
counter = CounterApplication(ml_model, line_points)

def inference(frame):
    frame = counter.count(frame)
    image = frame[35:89, 1431:1855]
    retval, img = cv2.threshold(image, 225, 255, cv2.THRESH_BINARY)
    img = cv2.GaussianBlur(img, (11, 11), 0)
    img = cv2.medianBlur(img, 9)
    pil_image = Image.fromarray(img)
    text = pytesseract.image_to_string(pil_image, config=r'--psm 7 --oem 3 -l eng -c tessedit_char_whitelist=0123456789')
    print(text)
    return frame

def consume_kafka_stream():
    # Set your Kafka broker address
    bootstrap_servers = 'localhost:9092'
    topic = 'videostreaming'

    consumer = KafkaConsumer(topic,
                             bootstrap_servers=bootstrap_servers,
                             group_id='video-consumer-group')

    print("connected to kafka broker")

    try:
        for message in consumer:
            frame_bytes = bytearray(message.value)
            frame_np = np.frombuffer(frame_bytes, dtype=np.uint8)
            frame = cv2.imdecode(frame_np, cv2.IMREAD_COLOR)

            # Perform inference on the frame
            inference_result = inference(frame)

            # Print or save the inference result
            print(inference_result)

    except KeyboardInterrupt:
        # Handle keyboard interrupt (Ctrl+C) gracefully
        print("Quitting gracefully")
        pass

    finally:
        # Close the Kafka consumer when done
        consumer.close()

if __name__ == "__main__":
    consume_kafka_stream()
