import numpy as np
import cv2
import time
import math

# Uses the first line of the camera image to determine whether we should go left or right. Camera is angled and pointed forward, at a slight height above the ground


class VisionHandler:
    m_lower_range_guide = np.array([85, 100, 50])
    m_upper_range_guide = np.array([150, 255, 255])

    m_lower_range_tree = np.array([85, 100, 50])
    m_upper_range_tree = np.array([150, 255, 255])

    m_lower_range_hand = np.array([85, 100, 50])
    m_upper_range_hand = np.array([150, 255, 255])

    crop_from_top = 0
    tree_stop_distance = 50

    go_left_size = 50
    end_reached_size = 150  # if the white doesn't start before this height, end reached, so turn around

    direction = 0
    turn_around = False
    tree_detected = False

    can_see_trees = True
    can_see_end = True
    stop_turning = False
    do_stop_check = False

    distance_to_guide = 0

    time_at_last_detection = 0

    angle = 0

    def __init__(self, video_source=0):
        # Open the video source
        self.cap = cv2.VideoCapture(video_source)
        if not self.cap.isOpened():
            raise ValueError("Unable to open video source", video_source)

        # Get video source width and height
        self.width = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)

    def update(self, ranges, go_left_size=50, no_gui=False):
        self.m_lower_range_guide = ranges[0][0]
        self.m_upper_range_guide = ranges[0][1]
        self.m_lower_range_tree = ranges[1][0]
        self.m_upper_range_tree = ranges[1][1]
        self.m_lower_range_hand = ranges[2][0]
        self.m_upper_range_hand = ranges[2][1]

        self.go_left_size = go_left_size
        if self.cap.isOpened():
            ret, frame = self.cap.read()
            frame = cv2.flip(frame, -1)
            rgb = np.copy(frame)
            rgb = self.normalize_colors(rgb)
            thresh = self.find_edge(rgb)
            trees = self.find_tree(rgb, frame)
            return True, [cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), thresh, trees, frame, frame]
        else:
            return False, None

    def normalize_colors(self, frame):
        output_frame = np.copy(frame)

        return output_frame

    def find_edge(self, frame):
        hsv = cv2.cvtColor(frame, cv2.cv2.COLOR_BGR2HSV)  # convert the frame to HSV color space
        mask = cv2.inRange(hsv, self.m_lower_range_guide, self.m_upper_range_guide)  # create mask for blue color
        mask = cv2.GaussianBlur(mask, (11, 11), cv2.BORDER_DEFAULT)  # blur the mask for better reading
        success, thresh = cv2.threshold(mask, 127, 255, cv2.THRESH_BINARY)
        self.distance_to_guide = mask.shape[0]
        distances = []

        first_y = -1
        for x in range(1, 361, 30):
            for line in range(frame.shape[0] - 1, self.end_reached_size - x, -1):
                # check if the first line is white
                if thresh[line, x] > 0:
                    dist = 480-line
                    if line > 1:
                        if first_y == -1:
                            first_y = dist
                        distances.append(dist - first_y)
                    break
        if len(distances) >= 2 and self.time_at_last_detection + 0.8 < time.time(): #wait at least a second before stopping turn
            averageDeltaY = 0
            for i in range(1, len(distances)):
                averageDeltaY += distances[i] - distances[i-1]
            averageDeltaY /= len(distances)
            averageDelta = averageDeltaY/(360/len(distances))
            new_angle = math.atan(averageDelta)
            self.angle = self.angle * 0.5 + new_angle * 57 * 0.5
            if 13.0 < self.angle < 15.0 and self.do_stop_check:
                self.stop_turning = True
                print("Stop turning", self.angle)
            if self.do_stop_check is False:
                self.stop_turning = False
            # self.distance_to_guide = sum(distances)/len(distances)

        self.distance_to_guide = first_y
        print(f'{self.angle}\r', end="")

        if self.go_left_size < self.distance_to_guide < self.end_reached_size:
            self.go_left()
        elif self.distance_to_guide <= self.go_left_size:
            self.go_right()
        else:
            self.direction = 0
            self.end_reached()

        return thresh

    def find_tree(self, frame, draw_frame):
        hsv = cv2.cvtColor(frame, cv2.cv2.COLOR_BGR2HSV)  # convert the frame to HSV color space
        mask = cv2.inRange(hsv, self.m_lower_range_tree, self.m_upper_range_tree)
        mask = cv2.GaussianBlur(mask, (11, 11), cv2.BORDER_DEFAULT)  # blur the mask for better reading
        success, thresh = cv2.threshold(mask, 127, 255, cv2.THRESH_BINARY)
        contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE,
                                               cv2.CHAIN_APPROX_SIMPLE)  # calculate the contours
        trees = []
        for i in range(len(contours)):  # loop trough all contours
            c = contours[i]
            if cv2.contourArea(c) <= 3000:  # discard contour if its too small
                continue
            else:
                # create a rectangle from the contour
                rect = cv2.minAreaRect(c)
                if rect[0][1] > self.crop_from_top:
                    trees.append(rect)
        for tree in trees:
            box = cv2.boxPoints(tree)
            box = np.int0(box)
            cv2.drawContours(draw_frame, [box], 0, (100, 90, 90), 2)
            if tree[0][0] < self.tree_stop_distance:
                self.tree_found()

        return thresh

    def go_left(self):
        self.direction = 1

    def go_right(self):
        self.direction = -1

    def tree_found(self):
        if self.can_see_trees and self.turn_around is False and self.time_at_last_detection + 3 < time.time() and self.can_see_end:
            self.tree_detected = True
            self.can_see_trees = False

    def end_reached(self):
        if self.can_see_end and self.time_at_last_detection + 5 < time.time():
            self.turn_around = True
            self.can_see_end = False
            self.time_at_last_detection = time.time()
        else:
            self.go_left()

VisionHandler(video_source=0)
