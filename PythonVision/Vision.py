import numpy as np
import cv2
import Transform


cap = cv2.VideoCapture(0)
lower_range = np.array([85, 100, 50])
upper_range = np.array([150, 255, 255])
cameraOrientation = True
keepDistanceToLine = 200


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


def singleGuide(guide):
    centerGuide = findCenter(guide)  # find the center of the guide
    leftGuide = centerGuide[0] < width / 2  # check whether the guide is left side or right side
    distance = abs(centerGuide[0] - width / 2)  # get distance to center from guide
    if leftGuide:
        if distance > keepDistanceToLine:
            goLeft()
        else:
            goRight()
        cv2.circle(robotVision, (int(centerGuide[0] + keepDistanceToLine), int(frame.shape[0] / 2)), 8,
                   (0, 0, 255), 2)  # draw a circle at the robots position
    else:
        if distance < keepDistanceToLine:
            goLeft()
        else:
            goRight()
        cv2.circle(robotVision, (int(centerGuide[0] - keepDistanceToLine), int(frame.shape[0] / 2)), 8, (0, 0, 255), 2)


def multipleGuides(guideLeft, guideRight):
    centerGuideLeft = findCenter(guideLeft)
    centerGuideRight = findCenter(guideRight)
    distance = abs(centerGuideLeft[0] - centerGuideRight[0])
    distToCenter = 0
    if centerGuideLeft[0] < width / 2:
        distToCenter = width / 2 - centerGuideLeft[0]
        cv2.circle(robotVision, (int(centerGuideLeft[0] + distance / 2), int(frame.shape[0] / 2)), 8,
                   (0, 0, 255), 2)
    else:
        distToCenter = width / 2 - centerGuideRight[0]
        cv2.circle(robotVision, (int(centerGuideRight[0] + distance / 2), int(frame.shape[0] / 2)), 8,
                   (0, 0, 255), 2)
    if distToCenter > distance / 2:
        goLeft()
    elif distToCenter < distance / 2:
        goRight()
    m_boxLeft = cv2.boxPoints(guideLeft)
    m_boxLeft = np.int0(m_boxLeft)
    ptsLeftRect = Transform.order_points(m_boxLeft)
    m_boxRight = cv2.boxPoints(guideRight)
    m_boxRight = np.int0(m_boxRight)
    ptsRightRect = Transform.order_points(m_boxRight)
    setWarp(ptsLeftRect[0], ptsLeftRect[3], ptsRightRect[1], ptsRightRect[2])


def setWarp(c1, c2, c3, c4):
    pts = np.array([(c1[0], c1[1]), (c2[0], c2[1]), (c3[0], c3[1]), (c4[0], c4[1])])
    global robotVision
    robotVision = Transform.four_point_transform(contourIm, pts)


def checkVertical(con):
    longSideAngle = 0
    if con[1][0] < con[1][1]:
        longSideAngle = con[2] + 180
    else:
        longSideAngle = con[2] + 90
    if (0 < longSideAngle < 45) or 135 < longSideAngle < 180:
        return True
    else:
        return False


def findCenter(con):
    return con[0]


while True:
    # Capture frame-by-frame
    ret, frame = cap.read()

    # Our operations on the frame come here
    rgb = frame
    hsv = cv2.cvtColor(frame, cv2.cv2.COLOR_BGR2HSV)  # convert the frame to HSV color space
    mask = cv2.inRange(hsv, lower_range, upper_range)  # create mask for blue color
    mask = cv2.GaussianBlur(mask, (11, 11), cv2.BORDER_DEFAULT)  # blur the mask for better reading
    success, thresh = cv2.threshold(mask, 127, 255, 0)  # create threshold map from mask
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)  # calculate the contours
    contourIm = np.zeros_like(rgb)  # create empty mask
    robotVision = np.zeros_like(rgb)  # create empty mask

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
                    multipleGuides(guidesLeft[0], guidesRight[0])
                elif len(guidesLeft) > 0:
                    print("Only left found")
                    singleGuide(guidesLeft[0])
                else:
                    print("Only right found")
                    singleGuide(guidesRight[0])

            # Display the resulting frame

    cv2.line(contourIm, (int(frame.shape[1] / 2), 0), (int(frame.shape[1] / 2), frame.shape[0]), (255, 0, 0), 3)
    cv2.imshow('frame', rgb)
    cv2.imshow('mask', mask)
    cv2.imshow('contour', contourIm)
    cv2.imshow('robotVision', robotVision)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
