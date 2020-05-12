import numpy as np
import cv2

# Uses the first line of the camera image to determine whether we should go left or right. Camera is angled and pointed forward, at a slight height above the ground


def tree_found():
    print("Tree found")


def go_left():
    print("Go left")


def go_right():
    print("Go right")

def end_reached():
    print("Turn around")

class VisionHandler:
    m_lower_range_guide = np.array([85, 100, 50])
    m_upper_range_guide = np.array([150, 255, 255])

    m_lower_range_tree = np.array([85, 100, 50])
    m_upper_range_tree = np.array([150, 255, 255])

    crop_from_top = 150
    tree_stop_distance = 50

    go_left_size = 50
    end_reached_size = 150  # if the white doesn't start before this height, end reached, so turn around

    def __init__(self, video_source=0):
        # Open the video source
        self.cap = cv2.VideoCapture(video_source)
        if not self.cap.isOpened():
            raise ValueError("Unable to open video source", video_source)

        # Get video source width and height
        self.width = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        self.update()

    def update(self, lower_range_guide=m_lower_range_guide, upper_range_guide=m_upper_range_guide, lower_range_tree=m_lower_range_tree, upper_range_tree=m_upper_range_tree,go_left_size=50):
        self.m_lower_range_guide = lower_range_guide
        self.m_upper_range_guide = upper_range_guide
        self.m_lower_range_tree = lower_range_tree
        self.m_upper_range_tree = upper_range_tree
        self.go_left_size = go_left_size
        if self.cap.isOpened():
            ret, frame = self.cap.read()
            thresh = self.find_edge(frame)
            trees = self.find_tree(frame)
            return True, [cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), thresh, trees, frame]
        else:
            return False, None

    def find_edge(self, frame):
        hsv = cv2.cvtColor(frame, cv2.cv2.COLOR_BGR2HSV)  # convert the frame to HSV color space
        mask = cv2.inRange(hsv, self.m_lower_range_guide, self.m_upper_range_guide)  # create mask for blue color
        mask = cv2.GaussianBlur(mask, (11, 11), cv2.BORDER_DEFAULT)  # blur the mask for better reading
        success, thresh = cv2.threshold(mask, 127, 255, cv2.THRESH_BINARY)
        distance_to_guide = mask.shape[0]
        for line in range(frame.shape[0] - 1, 0, -1):
            # check if the first line is white
            if thresh[line, 0] > 0:
                distance_to_guide = 480 - line
                break
        if self.end_reached_size > distance_to_guide > self.go_left_size:
            go_left()
        elif distance_to_guide <= self.go_left_size:
            go_right()
        else:
            end_reached()

        return thresh

    def find_tree(self, frame):
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
            cv2.drawContours(frame, [box], 0, (100, 90, 90), 2)
            if tree[0][0] < self.tree_stop_distance:
                tree_found()

        return thresh


VisionHandler(video_source=0)
