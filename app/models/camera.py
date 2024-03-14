from app.extensions import db
from sqlalchemy.sql import func
import json

class Camera(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    connection_url = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    state = db.Column(db.Boolean, default=False)
    line_points = db.Column(db.Text, nullable=True)
    polygon_points = db.Column(db.Text, nullable=True)
    alert_emails = db.Column(db.Text, nullable=True)
    image_path = db.Column(db.String(150), nullable=True)
    time_created = db.Column(db.DateTime(timezone=True), server_default=func.now())
    time_updated = db.Column(db.DateTime(timezone=True), onupdate=func.now())

    def set_line_points(self, points):
        self.line_points = json.dumps(points)

    def get_line_points(self):
        return json.loads(self.line_points) if self.line_points else []

    def set_polygon_points(self, points):
        self.polygon_points = json.dumps(points)

    def get_polygon_points(self):
        return json.loads(self.polygon_points) if self.polygon_points else []

    def set_alert_emails(self, emails):
        self.alert_emails = json.dumps(emails)

    def get_alert_emails(self):
        return json.loads(self.alert_emails) if self.alert_emails else []