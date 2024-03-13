import subprocess
from flask import Flask, request, render_template

app = Flask(__name__)

# Dictionary to store camera streams and their associated subprocesses
camera_processes = {}


def start_streaming(url):
    # Path to Python executable in the virtual environment
    python_exe = r'C:\Users\Prasanna P M\EC498_Major_Project\SurveilHub\.venv\Scripts\python.exe'

    # Start streaming subprocess for the given URL
    cmd = [python_exe, 'C:\\Users\\Prasanna P M\\EC498_Major_Project\\SurveilHub\\video_streaming\\producer.py', '--url', url] # Modify the command to include the URL parameter
    return subprocess.Popen(cmd)



def start_model_inference():
    # Start model inference subprocess
    cmd = ['python', 'model_inference_script.py']
    return subprocess.Popen(cmd)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_camera_stream', methods=['POST'])
def add_camera_stream():
    url = request.json.get('url')

    # Start streaming subprocess for the new camera
    streaming_process = start_streaming(url)

    # # Start model inference subprocess if not already running
    # if 'model_inference' not in camera_processes:
    #     model_inference_process = start_model_inference()
    #     camera_processes['model_inference'] = model_inference_process

    # Store the subprocess reference in the dictionary
    camera_processes[url] = streaming_process

    return 'Camera stream added successfully.'


@app.route('/remove_camera_stream', methods=['POST'])
def remove_camera_stream():
    url = request.json.get('url')

    # Terminate the streaming subprocess for the given URL
    streaming_process = camera_processes.pop(url, None)
    if streaming_process:
        streaming_process.terminate()

    return 'Camera stream removed successfully.'


if __name__ == '__main__':
    app.run(debug=True)
