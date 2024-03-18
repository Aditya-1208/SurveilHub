import argparse
from collections import defaultdict
from pathlib import Path

import cv2
import numpy as np
from shapely.geometry import Polygon
from shapely.geometry.point import Point

from ultralytics import YOLO
from ultralytics.utils.files import increment_path
from ultralytics.utils.plotting import Annotator, colors


class RegionCounter:
    def __init__(self, device="cpu", classes=None, line_thickness=2,
                 region_thickness=2):
        self.device = device
        self.classes = classes
        self.names = None
        self.im0 = None
        self.line_thickness = line_thickness
        self.track_thickness = 2
        self.draw_tracks = False
        self.region_thickness = region_thickness
        self.track_history = defaultdict(list)
        self.track_color = (0, 255, 0)
        self.annotator = None
        self.reg_pts = None
        self.counting_regions = []

    def set_args(self, classes_names, reg_pts, device=None, classes=None, line_thickness=None,
                region_thickness=None, draw_tracks=False, track_color=(0, 255, 0), track_thickness=2,
                ):

        if device:
            self.device = device
        if classes:
            self.classes = classes
        if line_thickness:
            self.line_thickness = line_thickness
        if region_thickness:
            self.region_thickness = region_thickness

        self.names = classes_names
        self.draw_tracks = draw_tracks
        self.track_color = track_color
        self.track_thickness = track_thickness
        self.reg_pts = reg_pts

        for pts in reg_pts:
            polygon = Polygon(pts)
            self.counting_regions.append({
                "polygon": polygon,
                "counts": 0,
                "tracked_ids": set(),
                "dragging": False,
                "region_color": (37, 255, 225),  
                "text_color": (0, 0, 0),  
            })
            print(f"Added polygon: {polygon}")


    def extract_and_process_tracks(self, tracks, im0, view_img=True):
        """
        Run Region counting on a video using YOLOv8 and ByteTrack.

        Supports movable region for real-time counting inside a specific area.
        Supports multiple regions counting.
        Regions can be Polygons or rectangles in shape.

        Args:
            tracks: Tracks data.
            im0: Input image frame.
            view_img: Whether to display the image.
        """
        boxes = tracks[0].boxes.xyxy.cpu()
        track_ids = tracks[0].boxes.id.int().cpu().tolist()
        clss = tracks[0].boxes.cls.cpu().tolist()

        annotator = Annotator(im0, line_width=self.line_thickness, example=str(self.names))

        for box, track_id, cls in zip(boxes, track_ids, clss):
            annotator.box_label(box, str(self.names[cls]), color=colors(cls, True))
            bbox_center = (box[0] + box[2]) / 2, (box[1] + box[3]) / 2  # Bbox center

            track = self.track_history[track_id] 
            track.append((float(bbox_center[0]), float(bbox_center[1])))
            if len(track) > 30:
                track.pop(0)

            if self.draw_tracks:
                annotator.draw_centroid_and_tracks(
                    track, color=self.track_color, track_thickness=self.track_thickness
                )

            points = np.hstack(track).astype(np.int32).reshape((-1, 1, 2))
            cv2.polylines(im0, [points], isClosed=False, color=colors(cls, True), thickness=self.track_thickness)

            # Check if detection inside region
            for region in self.counting_regions:
                if region["polygon"].contains(Point((bbox_center[0], bbox_center[1]))):
                    if track_id not in region["tracked_ids"]:
                        region["counts"] += 1
                        region["tracked_ids"].add(track_id)

                        # return self.im0 #saving/returnning frame which had intrusion
                        return True

        # Draw regions (Polygons/Rectangles)
        for region in self.counting_regions:
            region_label = str(region["counts"])
            region_color = region["region_color"]
            region_text_color = region["text_color"]

            polygon_coords = np.array(region["polygon"].exterior.coords, dtype=np.int32)
            centroid_x, centroid_y = int(region["polygon"].centroid.x), int(region["polygon"].centroid.y)

            text_size, _ = cv2.getTextSize(
                region_label, cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.7, thickness=self.line_thickness
            )
            text_x = centroid_x - text_size[0] // 2
            text_y = centroid_y + text_size[1] // 2
            cv2.rectangle(
                im0,
                (text_x - 5, text_y - text_size[1] - 5),
                (text_x + text_size[0] + 5, text_y + 5),
                region_color,
                -1,
            )
            cv2.putText(
                im0, region_label, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, region_text_color, self.line_thickness
            )
            cv2.polylines(im0, [polygon_coords], isClosed=True, color=region_color, thickness=self.region_thickness)

        return False
    def display_frames(self):
        cv2.imshow("Your Window Title", self.im0)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            return


        

    def start_counting(self, im0, tracks):
        self.im0 = im0
        # self.extract_and_process_tracks(tracks, im0)
        # self.display_frames() Uncomment this fucnction to see the cv2 window
        # return self.im0
        if self.extract_and_process_tracks(tracks, im0):
            return self.im0
        return None


