import os
from flask import Flask, request, jsonify, render_template, Response, send_from_directory, redirect, url_for

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


if __name__ == '__main__':
  app.run(debug=True)