import numpy as np
import cv2

cap = cv2.VideoCapture(0)
lower_range = np.array([85, 100, 50])
upper_range = np.array([150, 255, 255])


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
    hsv = cv2.cvtColor(frame, cv2.cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower_range, upper_range)
    mask = cv2.GaussianBlur(mask, (11, 11), cv2.BORDER_DEFAULT)
    success, thresh = cv2.threshold(mask, 127, 255, 0)
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contourIm = np.zeros_like(rgb)
    if len(contours) >= 2:
        guides = []
        contours.sort(reverse=True, key=contourSize)
        for i in range(len(contours)):
            c = contours[i]
            if cv2.contourArea(c) <= 300:
                continue
            else:
                rect = cv2.minAreaRect(c)
                box = cv2.boxPoints(rect)
                box = np.int0(box)
                cv2.drawContours(contourIm, [box], 0, (0, 0, 255), 2)
                guides.append(rect)
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
                    cv2.circle(contourIm, (int(centerGuideLeft[0] + distance / 2), int(frame.shape[0] / 2)), 8, (0, 0, 255), 2)
                else:
                    distToCenter = width / 2 - centerGuideRight[0]
                    cv2.circle(contourIm, (int(centerGuideRight[0] + distance / 2), int(frame.shape[0] / 2)), 8, (0, 0, 255), 2)

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
