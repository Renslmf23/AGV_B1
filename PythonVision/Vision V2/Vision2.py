import numpy as np
import cv2

# Uses the first line of the camera image to determine whether we should go left or right. Camera is angled and pointed forward, at a slight height above the ground


def go_left():
    print("Go left")


def go_right():
    print("Go right")


class VisionHandler:
    m_lower_range = np.array([85, 100, 50])
    m_upper_range = np.array([150, 255, 255])

    def __init__(self, video_source=0):
        # Open the video source
        self.cap = cv2.VideoCapture(video_source)
        if not self.cap.isOpened():
            raise ValueError("Unable to open video source", video_source)

        # Get video source width and height
        self.width = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)

    def update(self, lower_range=m_lower_range, upper_range=m_upper_range, go_left_size=50):
        if self.cap.isOpened():
            ret, frame = self.cap.read()
            orig = frame
            hsv = cv2.cvtColor(frame, cv2.cv2.COLOR_BGR2HSV)  # convert the frame to HSV color space
            mask = cv2.inRange(hsv, lower_range, upper_range)  # create mask for blue color
            mask = cv2.GaussianBlur(mask, (11, 11), cv2.BORDER_DEFAULT)  # blur the mask for better reading
            success, thresh = cv2.threshold(mask, 127, 255, 0)
            distance_to_guide = 0
            for line in range(mask.shape[0], 0):
                # check when the first line is white
                if np.mean(thresh[0, line], axis=2) < 127:
                    distance_to_guide = line
                    break
            print(distance_to_guide)
            if distance_to_guide > go_left_size:
                go_left()
            else:
                go_right()
            return True, [cv2.cvtColor(orig, cv2.COLOR_BGR2RGB), mask, thresh, orig]
        else:
            return False, None
