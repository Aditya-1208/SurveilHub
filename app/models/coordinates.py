from app.extensions import db
from sqlalchemy.sql import func

class Coordinates(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    