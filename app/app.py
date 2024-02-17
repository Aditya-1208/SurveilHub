import cv2
import imutils
from flask import Flask, render_template, Response
import numpy as np
import time
import threading
import queue

app = Flask(__name__)

# Set video file path (replace with your actual path)
VIDEO_PATH = "http://localhost:8080"

# Frame processing and display thread settings
FRAME_WIDTH = 400
FRAME_QUEUE_SIZE = 10
frame_queue = queue.Queue(maxsize=FRAME_QUEUE_SIZE)
# Global variables (use with caution)
fps = 0
TS = time.time()  # Initialize TS with current time
BREAK = False

def video_stream_gen():
    vid = cv2.VideoCapture(VIDEO_PATH)
    if not vid.isOpened():
        raise RuntimeError("Error opening video file")

    try:
        def frame_processor():
            while True:
                ret, frame = vid.read()
                if not ret:
                    break

                # Process frame (resize, etc.)
                frame = imutils.resize(frame, width=FRAME_WIDTH)

                try:
                    frame_queue.put(frame)
                except queue.Full:
                    # Handle queue overflow here (e.g., drop frame)
                    pass

        frame_processor_thread = threading.Thread(target=frame_processor)
        frame_processor_thread.start()

        while True:
            frame = frame_queue.get()

            # Encode frame for streaming (consider alternative techniques)
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
