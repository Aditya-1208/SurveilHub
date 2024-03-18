from ultralytics.utils.checks import check_imshow, check_requirements
from ultralytics.utils.plotting import Annotator, colors
import cv2
from collections import defaultdict
from utils.surveillance_applications.object_counter.onscreen import Annotator2
check_requirements("shapely>=2.0.0")

from shapely.geometry import LineString, Point, Polygon

class ObjectCounter:
    """A class to manage the counting of objects in a real-time video stream based on their tracks."""

    def __init__(self):
        """Initializes the Counter with default values for various tracking and counting parameters."""

        # Mouse events
        self.is_drawing = False
        self.selected_point = None

        # Region & Line Information
        self.reg_pts = [(1072, 568), (441, 426), (984, 161), (1279, 283)]
        self.line_dist_thresh = 15
        self.counting_region = None
        self.region_color = (255, 0, 255)
        self.region_thickness = 5

        # Image and annotation Information
        self.im0 = None
        self.tf = None
        self.view_img = False
        self.view_in_counts = True
        self.view_out_counts = True

        self.names = None  # Classes names
        self.annotator = None 
        self.annotator2 = None # Annotator


        self.in_counts = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0}
        self.out_counts = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0}
        self.counting_list = []
        self.count_txt_thickness = 0
        self.count_txt_color = (0, 0, 0)
        self.count_color = (255, 255, 255)

        # Tracks info
        self.track_history = defaultdict(list)
        self.track_thickness = 2
        self.draw_tracks = False
        self.track_color = (0, 255, 0)

        self.env_check = check_imshow(warn=True)

    def set_args(
        self,
        classes_names,
        reg_pts,
        count_reg_color=(255, 0, 255),
        line_thickness=2,
        track_thickness=2,
        view_img=False,
        view_in_counts=True,
        view_out_counts=True,
        draw_tracks=False,
        count_txt_thickness=1,
        count_txt_color=(0, 0, 0),
        count_color=(255, 255, 255),
        track_color=(0, 255, 0),
        region_thickness=5,
        line_dist_thresh=15,
    ):
        """
        Configures the Counter's image, bounding box line thickness, and counting region points.

        Args:
            line_thickness (int): Line thickness for bounding boxes.
            view_img (bool): Flag to control whether to display the video stream.
            view_in_counts (bool): Flag to control whether to display the incounts on video stream.
            view_out_counts (bool): Flag to control whether to display the outcounts on video stream.
            reg_pts (list): Initial list of points defining the counting region.
            classes_names (dict): Classes names
            track_thickness (int): Track thickness
            draw_tracks (Bool): draw tracks
            count_txt_thickness (int): Text thickness for object counting display
            count_txt_color (RGB color): count text color value
            count_color (RGB color): count text background color value
            count_reg_color (RGB color): Color of object counting region
            track_color (RGB color): color for tracks
            region_thickness (int): Object counting Region thickness
            line_dist_thresh (int): Euclidean Distance threshold for line counter
        """
        self.tf = line_thickness
        self.view_img = view_img
        self.view_in_counts = view_in_counts
        self.view_out_counts = view_out_counts
        self.track_thickness = track_thickness
        self.draw_tracks = draw_tracks

        if len(reg_pts) == 2:
            print("Line Counter Initiated.")
            self.reg_pts = reg_pts
            self.counting_region = LineString(self.reg_pts)

        self.names = classes_names
        self.track_color = track_color
        self.count_txt_thickness = count_txt_thickness
        self.count_txt_color = count_txt_color
        self.count_color = count_color
        self.region_color = count_reg_color
        self.region_thickness = region_thickness
        self.line_dist_thresh = line_dist_thresh


    def extract_and_process_tracks(self, tracks):
        boxes = tracks[0].boxes.xyxy.cpu()
        clss = tracks[0].boxes.cls.cpu().tolist()
        track_ids = tracks[0].boxes.id.int().cpu().tolist()

        self.annotator = Annotator(self.im0, self.tf, self.names)
        self.annotator.draw_region(reg_pts=self.reg_pts, color=self.region_color, thickness=self.region_thickness)

        for box, track_id, cls in zip(boxes, track_ids, clss):

            self.annotator.box_label(box, label=f"{track_id}:{self.names[cls]}", color=colors(int(cls), True))

            track_line = self.track_history[track_id]
            track_line.append((float((box[0] + box[2]) / 2), float((box[1] + box[3]) / 2)))
            if len(track_line) > 30:
                track_line.pop(0)

            if self.draw_tracks:
                self.annotator.draw_centroid_and_tracks(
                    track_line, color=self.track_color, track_thickness=self.track_thickness
                )

            prev_position = self.track_history[track_id][-2] if len(self.track_history[track_id]) > 1 else None

            if len(self.reg_pts) == 2:
                if prev_position is not None:
                    distance = Point(track_line[-1]).distance(self.counting_region)
                    if distance < self.line_dist_thresh and track_id not in self.counting_list:
                        self.counting_list.append(track_id)
                        self.in_counts[cls] += 1

        incount_labels = ["Count: "]
        for cls, count in self.in_counts.items():
            incount_labels.append(f"{self.names[cls]}: {count}|")

            # class name can be accessed by self.names[cls]
            # class count can be accessed by count (under this for loop)
            #this extract_and_process_tracks runs for each frame passed from start_counting function



        incount_str = ''.join(incount_labels)
        print(incount_str)



        if incount_str is not None:
            self.annotator.count_labels(
                counts=incount_str,  
                count_txt_size=self.count_txt_thickness,  
                txt_color=self.count_txt_color,
                color=self.count_color,
            )



    def display_frames(self):
        """Display frame."""
        if self.env_check:
            cv2.namedWindow("Ultralytics YOLOv8 Object Counter")
            if len(self.reg_pts) == 4: 
                cv2.setMouseCallback(
                    "Ultralytics YOLOv8 Object Counter", self.mouse_event_for_region, {"region_points": self.reg_pts}
                )
            cv2.imshow("Ultralytics YOLOv8 Object Counter", self.im0)
            # Break Window
            if cv2.waitKey(1) & 0xFF == ord("q"):
                return

    def start_counting(self, im0, tracks):
        """
        Main function to start the object counting process.

        Args:
            im0 (ndarray): Current frame from the video stream.
            tracks (list): List of tracks obtained from the object tracking process.
        """
        self.im0 = im0 

        if tracks[0].boxes.id is None:
            if self.view_img:
                self.display_frames()
            return im0
        self.extract_and_process_tracks(tracks)

        if self.view_img:
            self.display_frames()
        return self.im0