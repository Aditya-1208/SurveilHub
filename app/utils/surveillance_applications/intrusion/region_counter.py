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
        self.reg_pts = [(680, 257), (986, 125), (1174, 189), (930, 290)]
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
        polygon = Polygon(reg_pts)
        self.counting_regions.append({
            "name": "YOLOv8 Rectangle Region",
            "polygon": polygon,
            "counts": 0,
            "dragging": False,
            "region_color": (37, 255, 225),  # Red color for custom regions
            "text_color": (0, 0, 0),  # White text color for custom regions
        })
        print(f"Added polygon: {polygon}")


    def mouse_callback(self, event, x, y, flags, param):
        """
        Handles mouse events for region manipulation.

        Parameters:
            event (int): The mouse event type (e.g., cv2.EVENT_LBUTTONDOWN).
            x (int): The x-coordinate of the mouse pointer.
            y (int): The y-coordinate of the mouse pointer.
            flags (int): Additional flags passed by OpenCV.
            param: Additional parameters passed to the callback (not used in this function).

        Global Variables:
            current_region (dict): A dictionary representing the current selected region.

        Mouse Events:
            - LBUTTONDOWN: Initiates dragging for the region containing the clicked point.
            - MOUSEMOVE: Moves the selected region if dragging is active.
            - LBUTTONUP: Ends dragging for the selected region.

        Notes:
            - This function is intended to be used as a callback for OpenCV mouse events.
            - Requires the existence of the 'counting_regions' list and the 'Polygon' class.

        Example:
            >>> cv2.setMouseCallback(window_name, mouse_callback)
        """
        if event == cv2.EVENT_LBUTTONDOWN:
            for region in self.counting_regions:
                if region["polygon"].contains(Point((x, y))):
                    region["dragging"] = True
                    region["offset_x"] = x
                    region["offset_y"] = y
        elif event == cv2.EVENT_MOUSEMOVE:
            for region in self.counting_regions:
                if region["dragging"]:
                    dx = x - region["offset_x"]
                    dy = y - region["offset_y"]
                    region["polygon"] = Polygon(
                        [(p[0] + dx, p[1] + dy) for p in region["polygon"].exterior.coords]
                    )
                    region["offset_x"] = x
                    region["offset_y"] = y
        elif event == cv2.EVENT_LBUTTONUP:
            for region in self.counting_regions:
                region["dragging"] = False

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

            track = self.track_history[track_id]  # Tracking Lines plot
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
                    region["counts"] += 1

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

        # if view_img:
        #     cv2.imshow("Your Window Title", im0)
        #     cv2.waitKey(0)
        #     cv2.destroyAllWindows()

        # for region in self.counting_regions:  # Reinitialize count for each region
        #     region["counts"] = 0

    def display_frames(self):
        cv2.imshow("Your Window Title", self.im0)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            return


        

    def start_counting(self, im0, tracks):
        self.im0 = im0
        self.extract_and_process_tracks(tracks, im0)
        self.display_frames()
        return self.im0



