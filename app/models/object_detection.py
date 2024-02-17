from app.extensions import db
from sqlalchemy.sql import func

class ObjectDetection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    camera_id = db.Column(db.Integer, db.ForeignKey('camera.id'))
    predicted_class = db.Column(db.String(150))
    timestamp = db.Column(db.DateTime)
    additional_info = db.Column(db.Text)
    time_created = db.Column(db.DateTime(timezone=True), server_default=func.now())
    time_updated = db.Column(db.DateTime(timezone=True), onupdate=func.now())