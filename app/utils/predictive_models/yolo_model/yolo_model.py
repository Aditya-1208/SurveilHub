from utils.predictive_models.base_model import BaseModel
from ultralytics import YOLO

class YOLOModel(BaseModel):
    def __init__(self, model_path="best.pt"):
        super().__init__(model_path)
        self.model = YOLO(model_path)

    def names():
        return model.names
