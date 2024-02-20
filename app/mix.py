import numpy as np
from ultralytics import YOLO
import cv2
import cvzone
import math
from sort import *
import pandas as pd
from datetime import datetime, timedelta
import easyocr
import pytesseract
import os

reader = easyocr.Reader(['en'])
model = YOLO('best.pt')
tracker = Sort(max_age=10, min_hits=2, iou_threshold=0.3)
limits = [116, 122, 530, 205]
totalcount = []
start_time = datetime.now()



count_data = []
excel_file_name = None

# Set tesseract path
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Counter for frames
frame_count = 0

# Start time
video_start_time = time.time()

# Set to store logged times
logged_times = set()

cap = cv2.VideoCapture("output.mp4")
classNames = ['2-Wheeler', '2-axle', '3-axle-Commercial', 'LCV-LGV-Mini-Bus', 'Oversized-7-axle-', 'car', 'person']
detected_categories = ['category 1', 'category 2', 'category 3', 'category 4', 'category 5', 'category 6', 'category 7']
category_counts = {'category 1': 0,
                   'category 2': 0,
                   'category 3': 0,
                   'category 4': 0,
                   'category 5': 0,
                   'category 6': 0,
                   'category 7': 0
                   }
class_mapping = {
    "2-Wheeler": "category 1",
    "2-axle": "category 2",
    "3-axle-Commercial": "category 3",
    "LCV-LGV-Mini-Bus": "category 4",
    "Oversized-7-axle-": "category 5",
    "car": "category 6",
    "person": "category 7"
}
count_df = pd.DataFrame(columns=['date'] + ['Time'] + list(category_counts.keys()))

def map_class_name(original_class_name):
    return class_mapping.get(original_class_name, original_class_name)

while True:
    success, imag = cap.read()
    if not success:
        break

    img = cv2.resize(imag, (1080, 720))
    roi = img[10:350, 400:950]
    results = model(roi, show=True, conf=0.3)
    detection = np.empty((0, 5))

    for r in results:
        boxes = r.boxes
        for box in boxes:
            x1, y1, x2, y2 = box.xyxy[0]
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
            w, h = x2 - x1, y2 - y1
            conf = math.ceil((box.conf[0] * 100)) / 100
            cls = int(box.cls[0])
            if 0 <= cls < len(classNames):
                classfound = classNames[cls]
                if classfound == "Car/Jeep/Van/MV" or classfound == "LCV/LGV/MiniBus" or classfound == "2 axle" or \
                    classfound == "3 axle" or classfound == "4 to 6 axle" or classfound == "oversized" and conf > 0.3:
                    new_class_name = map_class_name(classfound)
                    currentArray = np.array([x1, y1, x2, y2, conf])
                    detection = np.vstack((detection, currentArray))

    tracker_results = tracker.update(detection)
    cv2.line(roi, (limits[0], limits[1]), (limits[2], limits[3]), (255, 0, 0), 3)

    for res in tracker_results:
        x1, y1, x2, y2, id = res
        x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
        w, h = x2 - x1, y2 - y1
        cvzone.cornerRect(roi, (x1, y1, w, h), l=9, rt=2, colorR=(255, 0, 255))
        cx, cy = x1 + w // 2, y1 + h // 2
        cv2.circle(roi, (cx, cy), 2, (255, 0, 255), cv2.FILLED)

        if limits[0] < cx < limits[2] and limits[1] - 5 < cy < limits[1] + 5:
            if totalcount.count(id) == 0:
                totalcount.append(id)
                
                # Extract time using Tesseract OCR
                gamer = img[:85, 800:]
                _, gamer = cv2.threshold(gamer, 210, 255, cv2.THRESH_BINARY)
                res = reader.readtext(gamer, detail=0, allowlist='0123456789- ')
                cleaned_string = res[0].replace('-', '').replace(' ', '')
                formatted_date = cleaned_string[:8]
                formatted_time = cleaned_string[8:]
                year, month, day = formatted_date[:4], formatted_date[4:6], formatted_date[6:]
                formatted_date = '-'.join([year, month, day])
                formatted_time = ':'.join([formatted_time[i:i+2] for i in range(0, len(formatted_time), 2)])

                current_time = datetime.now()
                elapsed_time = current_time - start_time

                if elapsed_time.total_seconds() >= 30:
                    start_time = current_time
                    count_row = {'Date': formatted_date, 'Time': formatted_time}
                    count_row.update(category_counts)
                    count_data.append(count_row)
                    category_counts = dict.fromkeys(category_counts, 0)

                    if excel_file_name is None:
                        excel_file_name = os.path.abspath(f'counts_{current_time.strftime("%Y%m%d_%H%M%S")}.xlsx')
                        os.makedirs(os.path.dirname(excel_file_name), exist_ok=True)
                        pd.DataFrame(count_data).to_excel(excel_file_name, index=False)
                    else:
                        with pd.ExcelWriter(excel_file_name, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
                            if 'Sheet1' not in writer.book.sheetnames:
                                pd.DataFrame(count_data).to_excel(writer, index=False, sheet_name='Sheet1')
                            else:
                                pd.DataFrame(count_data).to_excel(writer, index=False, header=False, sheet_name='Sheet1')

                    print(f'Counts saved to {excel_file_name}.')

    font = cv2.FONT_HERSHEY_SIMPLEX
    font_size = 0.5
    font_thickness = 1
    font_color = (255, 255, 255)

    y_coordinate = 50

    for category, count in category_counts.items():
        text = f"{category}: {count} "
        cv2.putText(img, text, (50, y_coordinate), font, font_size, font_color, font_thickness, cv2.LINE_AA)
        y_coordinate += 50

    cv2.imshow("Car Counter", img)

    key = cv2.waitKey(1) & 0xFF

    if key == ord('q'):
        break