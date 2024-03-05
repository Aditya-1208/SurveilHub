from utils.surveillance_applications.base_application import BaseApplication
from utils.surveillance_applications.object_counter.helper import *

class CounterApplication(BaseApplication):
    def __init__(self, inference_model):
        self.model = inference_model
        line_points = [(10, 400), (2000, 550)]  
        classes_to_count = [0, 1, 2, 3, 4, 5, 6] 
        counter = ObjectCounter()
        counter.set_args(view_img=True, reg_pts=line_points, classes_names=inference_model.names, draw_tracks=True)

    def count(self, frame):
        tracks = model.track(frame, persist=True, show=False, classes=classes_to_count)
        frame = counter.start_counting(frame, tracks)
        return frame
