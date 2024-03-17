from utils.surveillance_applications.base_application import BaseApplication
from utils.surveillance_applications.intrusion.region_counter import *

class IntrusionApplication(BaseApplication):
    def __init__(self, inference_model, line_points):
        self.model = inference_model
        self.classes_to_count = [0, 1, 2, 3, 4, 5, 6] 
        self.line_points = line_points
        self.counter = RegionCounter()
        self.counter.set_args(classes_names=inference_model.names(), reg_pts=self.line_points, draw_tracks=True)


    def count(self, frame):
        tracks = self.model.track(frame, persist=True, show=False, classes=self.classes_to_count)
        frame = self.counter.start_counting(frame, tracks)
        return frame