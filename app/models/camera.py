from app.extensions import db
from sqlalchemy.sql import func
import app
import json
import os
import cv2

class Camera(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    connection_url = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    state = db.Column(db.Boolean, default=False)
    regions = db.Column(db.Text, nullable=True)
    region_colors = db.Column(db.Text, nullable=True)
    alert_emails = db.Column(db.Text, nullable=True)
    image_path = db.Column(db.String(150), nullable=True)
    time_created = db.Column(db.DateTime(timezone=True), server_default=func.now())
    time_updated = db.Column(db.DateTime(timezone=True), onupdate=func.now())

    def set_regions(self, points):
        self.regions = "[]" if not points else json.dumps(points)

    def get_regions_innermost_tuple_string(self):
        if self.regions:
            regions_string = json.loads(self.regions)
            depth = 0
            result = ""
            for char in regions_string:
                if char == '[':
                    depth += 1
                    if depth == 3:  # Check if it's the innermost '['
                        result += '('
                    else:
                        result += char
                elif char == ']':
                    if depth == 3:  # Check if it's the innermost ']'
                        result += ')'
                    else:
                        result += char
                    depth -= 1
                else:
                    result += char
            return result
        else:
            return "[]"

    def get_regions(self):
        return json.loads(self.regions) if self.regions else []

    def set_region_colors(self, points):
        self.region_colors = "[]" if not points else json.dumps(points)

    def get_region_colors(self):
        return json.loads(self.region_colors) if self.region_colors else []

    def get_alert_emails(self):
        return [element.strip() for element in self.alert_emails.split(',')] if self.alert_emails else []

    def get_alert_emails_string(self):
        return f"{self.get_alert_emails()}"

    def capture_frame(self):
        # Open connection to camera
        cap = cv2.VideoCapture(self.connection_url)

        # Capture frame-by-frame
        ret, frame = cap.read()

        if ret:
            # Save the frame
            save_path = os.path.join(os.path.dirname(__file__),'..','static', 'camera','reference_images', f'frame{self.id}.jpg')
            print(save_path)
            cv2.imwrite(save_path, frame)
            self.image_path = f'frame{self.id}.jpg'
            db.session.commit()
            print("Image saved successfully.")
        else:
            print("Failed to capture frame.")