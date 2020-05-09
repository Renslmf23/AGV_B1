import numpy as np
import cv2

cap = cv2.VideoCapture(0)
lower_range = np.array([85, 100, 50])
upper_range = np.array([150, 255, 255])
cameraOrientation = True
keepDistanceToLine = 200


def contourSize(e):
    return cv2.contourArea(e)


def goLeft():
    print("Go left")


def goRight():
    print("Go right")


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
        if len(guides) == 1:  # if there is only one contour that qualifies as guide, e.g. on the edges
            guide = guides[0]
            if checkVertical(guide) is cameraOrientation:  # check if the contour is a stop or not
                centerGuide = findCenter(guide)  # find the center of the guide
                width = frame.shape[1]  # get screen width
                leftGuide = centerGuide[0] < width / 2  # check whether the guide is left side or right side
                distance = abs(centerGuide[0] - width / 2)  # get distance to center from guide
                if leftGuide:
                    if distance > keepDistanceToLine:
                        goLeft()
                    else:
                        goRight()
                    cv2.circle(contourIm, (int(centerGuide[0] + keepDistanceToLine), int(frame.shape[0] / 2)), 8,
                               (0, 0, 255), 2)  # draw a circle at the robots position
                else:
                    if distance < keepDistanceToLine:
                        goLeft()
                    else:
                        goRight()
                    cv2.circle(contourIm, (int(centerGuide[0] - keepDistanceToLine), int(frame.shape[0] / 2)), 8,
                               (0, 0, 255), 2)  # draw a circle at the robots position
        if len(guides) >= 2:
            useBothGuides = bordersFound = True
            guideLeft = guides[0]
            if checkVertical(guideLeft) is False:
                useBothGuides = False
            guideRight = guides[1]
            if checkVertical(guideRight) is False:
                if useBothGuides is False:
                    bordersFound = False
                else:
                    useBothGuides = False
            if bordersFound:
                centerGuideLeft = findCenter(guideLeft)
                centerGuideRight = findCenter(guideRight)
                distance = abs(centerGuideLeft[0] - centerGuideRight[0])
                width = frame.shape[1]
                distToCenter = 0
                if centerGuideLeft[0] < width / 2:
                    distToCenter = width / 2 - centerGuideLeft[0]
                    cv2.circle(contourIm, (int(centerGuideLeft[0] + distance / 2), int(frame.shape[0] / 2)), 8,
                               (0, 0, 255), 2)
                else:
                    distToCenter = width / 2 - centerGuideRight[0]
                    cv2.circle(contourIm, (int(centerGuideRight[0] + distance / 2), int(frame.shape[0] / 2)), 8,
                               (0, 0, 255), 2)

                if distToCenter > distance / 2:
                    goLeft()
                elif distToCenter < distance / 2:
                    goRight()
            # Display the resulting frame

    cv2.line(contourIm, (int(frame.shape[1] / 2), 0), (int(frame.shape[1] / 2), frame.shape[0]), (255, 0, 0), 3)
    cv2.imshow('frame', rgb)
    cv2.imshow('mask', mask)
    cv2.imshow('contour', contourIm)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
