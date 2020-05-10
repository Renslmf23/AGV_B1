import numpy as np
import cv2
import Transform


def contourSize(e):
    return cv2.contourArea(e)


def rectSize(r):
    return r[1][0] * r[1][1]


def goLeft():
    # print("Go left")
    return


def goRight():
    # print("Go right")
    return


def stop():
    # print("End reached")
    return


def singleGuide(guide, keep_distance, input_frame):
    width = input_frame.shape[1]
    height = input_frame.shape[0]
    outputFrame = np.zeros_like(input_frame)
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
    outputFrame = np.zeros_like(input_frame)
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
        cv2.circle(outputFrame, (int(centerGuideRight[0] + distance / 2), int(height / 2)), 8,
                   (0, 0, 255), 2)
    if distToCenter > distance / 2:
        goLeft()
    elif distToCenter < distance / 2:
        goRight()
    m_boxLeft = cv2.boxPoints(guide_left)
    m_boxLeft = np.int0(m_boxLeft)
    ptsLeftRect = Transform.order_points(m_boxLeft)
    m_boxRight = cv2.boxPoints(guide_right)
    m_boxRight = np.int0(m_boxRight)
    ptsRightRect = Transform.order_points(m_boxRight)
    return setWarp(ptsLeftRect[0], ptsLeftRect[3], ptsRightRect[1], ptsRightRect[2], outputFrame)


def setWarp(c1, c2, c3, c4, input_frame):
    pts = np.array([(c1[0], c1[1]), (c2[0], c2[1]), (c3[0], c3[1]), (c4[0], c4[1])])
    return Transform.four_point_transform(input_frame, pts)


def checkVertical(con):
    longSideAngle = 0
    if con[1][0] < con[1][1]:
        longSideAngle = con[2] + 180
    else:
        longSideAngle = con[2] + 90
    # print("Angle: ", longSideAngle)
    if (0 < longSideAngle < 70) or 110 < longSideAngle < 180:
        return True
    else:
        return False


def findCenter(con):
    return con[0]


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

    def update(self, lower_range=m_lower_range, upper_range=m_upper_range, requested_frame=0):  #
        if self.cap.isOpened():
            ret, frame = self.cap.read()

            rgb = frame
            hsv = cv2.cvtColor(frame, cv2.cv2.COLOR_BGR2HSV)  # convert the frame to HSV color space
            mask = cv2.inRange(hsv, lower_range, upper_range)  # create mask for blue color
            mask = cv2.GaussianBlur(mask, (11, 11), cv2.BORDER_DEFAULT)  # blur the mask for better reading
            success, thresh = cv2.threshold(mask, 127, 255, 0)  # create threshold map from mask
            contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE,
                                                   cv2.CHAIN_APPROX_SIMPLE)  # calculate the contours
            contourIm = np.zeros_like(rgb)  # create empty mask
            finalFrame = np.zeros_like(rgb)  # create empty mask

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
                        cv2.drawContours(contourIm, [box], 0, (0, 0, 255), 2)
                        guides.append(rect)  # and add it to the guides
                if len(guides) >= 1:  # multiple guides found
                    verticalGuides = []
                    horizontalGuides = []
                    width = frame.shape[1]
                    for guide in guides:
                        if checkVertical(guide):
                            verticalGuides.append(guide)
                        else:
                            horizontalGuides.append(guide)

                    if len(horizontalGuides) > 0:
                        stop()
                    if len(verticalGuides) >= 2:
                        guidesLeft = []
                        guidesRight = []
                        for guide in verticalGuides:
                            if findCenter(guide)[0] < width / 2:
                                guidesLeft.append(guide)
                            else:
                                guidesRight.append(guide)
                        guidesLeft.sort(reverse=True, key=rectSize)
                        guidesRight.sort(reverse=True, key=rectSize)
                        if len(guidesLeft) > 0 and len(guidesRight) > 0:
                            print("Both guides found")
                            finalFrame = multipleGuides(guidesLeft[0], guidesRight[0], contourIm)
                        elif len(guidesLeft) > 0:
                            print("Only left found")
                            finalFrame = singleGuide(guidesLeft[0], self.keepDistanceToLine, contourIm)
                        else:
                            print("Only right found")
                            finalFrame = singleGuide(guidesRight[0], self.keepDistanceToLine, contourIm)

                    # Display the resulting frame

            cv2.line(finalFrame, (int(frame.shape[1] / 2), 0), (int(frame.shape[1] / 2), frame.shape[0]), (255, 0, 0),
                     3)
            if requested_frame == 0:
                return True, cv2.cvtColor(rgb, cv2.COLOR_BGR2RGB)
            elif requested_frame == 1:
                return True, mask
            elif requested_frame == 2:
                return True, contourIm
            elif requested_frame == 3:
                return True, finalFrame
            else:
                return True, [cv2.cvtColor(rgb, cv2.COLOR_BGR2RGB), mask, contourIm, finalFrame]
        else:
            return False, None

    def __del__(self):
        if self.cap.isOpened():
            self.cap.release()
            cv2.destroyAllWindows()
