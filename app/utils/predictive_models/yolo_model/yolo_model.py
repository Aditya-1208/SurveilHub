from utils.predictive_models.base_model import BaseModel
from ultralytics import YOLO
import os

class YOLOModel(BaseModel):
    def __init__(self, model_path=os.path.join(os.path.dirname(__file__), 'best.pt') ):
        super().__init__(model_path)
        self.model = YOLO(model_path)

    def names():
        return model.names

    def track(self, frame, persist=True, show=False, classes=None):
        return self.model.track(frame, persist=persist, show=show, classes=classes)
