import numpy as np
import cv2
import time

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

    distance_to_guide = 0

    time_at_last_detection = 0

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
            hand = self.find_hand(rgb, frame)

            return True, [cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), thresh, trees, rgb, frame]
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
        for line in range(frame.shape[0] - 1, 0, -1):
            # check if the first line is white
            if thresh[line, 50] > 0:
                self.distance_to_guide = 480 - line
                break
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
            if cv2.contourArea(c) <= 300:  # discard contour if its too small
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

    def find_hand(self, frame, draw_frame):
        hsv = cv2.cvtColor(frame, cv2.cv2.COLOR_BGR2HSV)  # convert the frame to HSV color space
        mask = cv2.inRange(hsv, self.m_lower_range_hand, self.m_upper_range_hand)
        mask = cv2.GaussianBlur(mask, (11, 11), cv2.BORDER_DEFAULT)  # blur the mask for better reading
        success, thresh = cv2.threshold(mask, 127, 255, cv2.THRESH_BINARY)
        contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE,
                                               cv2.CHAIN_APPROX_SIMPLE)  # calculate the contours
        hand = []
        for i in range(len(contours)):  # loop trough all contours
            c = contours[i]
            if cv2.contourArea(c) <= 10000:  # discard contour if its too small
                continue
            else:
                # create a rectangle from the contour
                rect = cv2.minAreaRect(c)
                box = cv2.boxPoints(rect)
                box = np.int0(box)
                cv2.drawContours(draw_frame, [box], 0, (100, 90, 90), 2)
        return thresh

    def go_left(self):
        self.direction = 1
        # print("Go left")

    def go_right(self):
        self.direction = -1
        # print("Go right")

    def tree_found(self):
        if self.can_see_trees:
            self.tree_detected = True
            self.can_see_trees = False
            print("Tree found")

    def end_reached(self):
        if self.can_see_end:
            print("End reached")
            self.turn_around = True
            self.can_see_end = False


        # print("Turn around")


VisionHandler(video_source=0)
