from utils.surveillance_applications.base_application import BaseApplication
from utils.surveillance_applications.object_counter.line_counter import *

class CounterApplication(BaseApplication):
    def __init__(self, inference_model, line_points):
        self.model = inference_model
        self.classes_to_count = [0, 1, 2, 3, 4, 5, 6] 
        line_points = line_points
        self.counter = ObjectCounter()
        self.counter.set_args(view_img=True, reg_pts=line_points, classes_names=inference_model.names(), draw_tracks=True)

    def count(self, frame):
        tracks = self.model.track(frame, persist=True, show=False, classes=self.classes_to_count)
        frame = self.counter.start_counting(frame, tracks)
        return frame