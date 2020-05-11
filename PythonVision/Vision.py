import numpy as np
import cv2
import Transform


def contourSize(e):
    return cv2.contourArea(e)


def rectSize(r):
    return r[1][0] * r[1][1]


def goLeft():
    print("Go left")
    return


def goRight():
    print("Go right")
    return


def stop():
    # print("End reached")
    return


def singleGuide(guide, keep_distance, input_frame):
    width = input_frame.shape[1]
    height = input_frame.shape[0]
    outputFrame = input_frame
    centerGuide = findCenter(guide)  # find the center of the guide
    leftGuide = centerGuide[0] < width / 2  # check whether the guide is left side or right side
    distance = abs(centerGuide[0] - width / 2)  # get distance to center from guide
    if leftGuide:
        if distance > keep_distance:
            goLeft()
        else:
            goRight()
        cv2.circle(outputFrame, (int(centerGuide[0] + keep_distance), int(height / 2)), 8,
                   (0, 0, 255), 2)  # draw a circle at the robots position
    else:
        if distance < keep_distance:
            goLeft()
        else:
            goRight()
        cv2.circle(outputFrame, (int(centerGuide[0] - keep_distance), int(height / 2)), 8, (0, 0, 255), 2)
    return outputFrame


def multipleGuides(guide_left, guide_right, input_frame):
    width = input_frame.shape[1]
    height = input_frame.shape[0]
    outputFrame = input_frame
    centerGuideLeft = findCenter(guide_left)
    centerGuideRight = findCenter(guide_right)
    distance = abs(centerGuideLeft[0] - centerGuideRight[0])
    distToCenter = 0
    if centerGuideLeft[0] < width / 2:
        distToCenter = width / 2 - centerGuideLeft[0]
        cv2.circle(outputFrame, (int(centerGuideLeft[0] + distance / 2), int(height / 2)), 8,
                   (0, 0, 255), 2)
    else:
        distToCenter = width / 2 - centerGuideRight[0]
        cv2.circle(outputFrame, (int(centerGuideRight[0] - distance / 2), int(height / 2)), 8,
                   (0, 0, 255), 2)
    if distToCenter > distance / 2:
        goLeft()
    elif distToCenter < distance / 2:
        goRight()

    return outputFrame
    # coordinates = np.array([ptsLeftRect[0], [ptsLeftRect[3][0], height], ptsRightRect[1], [ptsRightRect[2][0], height]], np.float32)


def warp(input_frame):
    width = input_frame.shape[1]
    height = input_frame.shape[0]
    coordinates = np.array([[74, 300], [0, height - 100], [width-74, 300], [width, height - 100]], np.float32)
    target_coordinates = np.array([[0, 0], [0, height], [width, 0], [width, height]], np.float32)
    M = cv2.getPerspectiveTransform(coordinates, target_coordinates)
    warp_frame = cv2.warpPerspective(input_frame, M, (width, height))
    return warp_frame


def checkVertical(con):
    longSideAngle = 0
    if con[1][0] < con[1][1]:
        longSideAngle = con[2] + 180
    else:
        longSideAngle = con[2] + 90
    # print("Angle: ", longSideAngle)
    if (0 < longSideAngle < 45) or 135 < longSideAngle < 180:
        return True
    else:
        return False


def findCenter(con):
    return con[0]

def find_area(con):
    return con[1][0] * con[1][1]


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
        self.cameraOrientation = True
        self.keepDistanceToLine = 200

    def update(self, lower_range=m_lower_range, upper_range=m_upper_range, go_left_size=500):  #
        if self.cap.isOpened():
            ret, frame = self.cap.read()
            if frame is not None:
                rgb = frame
                hsv = cv2.cvtColor(frame, cv2.cv2.COLOR_BGR2HSV)  # convert the frame to HSV color space
                mask = cv2.inRange(hsv, lower_range, upper_range)  # create mask for blue color
                mask = cv2.GaussianBlur(mask, (11, 11), cv2.BORDER_DEFAULT)  # blur the mask for better reading
                success, thresh = cv2.threshold(mask, 127, 255, 0)  # create threshold map from mask
                contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE,
                                                       cv2.CHAIN_APPROX_SIMPLE)  # calculate the contours
                robot_vision = np.zeros_like(rgb)
                if len(contours) > 0:  # if we found contours...
                    guides = []
                    contours.sort(reverse=True, key=contourSize)  # sort the contours by area
                    for i in range(len(contours)):  # loop trough all contours
                        c = contours[i]
                        if cv2.contourArea(c) <= 300:  # discard contour if its too small
                            continue
                        else:
                            # create a rectangle from the contour
                            rect = cv2.minAreaRect(c)
                            box = cv2.boxPoints(rect)
                            box = np.int0(box)
                            cv2.drawContours(robot_vision, [box], 0, (100, 90, 90), 2)
                            cv2.drawContours(rgb, [box], 0, (100, 90, 90), 2)
                            cv2.fillPoly(mask, pts=[box], color=(150, 255, 255))
                            guides.append(rect)  # and add it to the guides
                    if len(guides) >= 1:  # multiple guides found
                        verticalGuides = []
                        horizontalGuides = []
                        width = frame.shape[1]
                        for guide in guides:
                            if checkVertical(guide) is False:
                                horizontalGuides.append(guide)

                        if len(horizontalGuides) > 0:
                            # found guide
                            if find_area(horizontalGuides[0]) > go_left_size:
                                goLeft()
                            else:
                                goRight()


                        # Display the resulting frame

            cv2.line(robot_vision, (int(frame.shape[1] / 2), 0), (int(frame.shape[1] / 2), frame.shape[0]), (255, 0, 0),
                     3)
            return True, [cv2.cvtColor(rgb, cv2.COLOR_BGR2RGB), mask, robot_vision, thresh]
        else:
            return False, None

    def __del__(self):
        if self.cap.isOpened():
            self.cap.release()
            cv2.destroyAllWindows()
