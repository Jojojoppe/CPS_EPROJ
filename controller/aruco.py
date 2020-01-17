import time
import cv2
import cv2.aruco as aruco
import numpy as np

from picamera.array import PiRGBArray
from picamera import PiCamera

camera = PiCamera()
camera.resolution = (320, 240)
camera.framerate = 32
rawCapture = PiRGBArray(camera, size=(320, 240))

time.sleep(0.1)

lower = np.array([50])
upper = np.array([255])
kernel = np.ones((5,5), np.uint8)

for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    image = frame.array
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    aruco_dict = aruco.Dictionary_get(aruco.DICT_6X6_250)
    parameters = aruco.DetectorParameters_create()
    corners,ids,rejectedImgPoints = aruco.detectMarkers(gray, aruco_dict, parameters=parameters)
    print(corners, ids)

    marker = aruco.drawDetectedMarkers(gray, corners)

    erdil = cv2.erode(gray, kernel, iterations=5)
    erdil = cv2.dilate(erdil, kernel, iterations=5)

    mask = cv2.inRange(erdil, lower, upper)
    mask = cv2.bitwise_not(mask)
    ret, thresh = cv2.threshold(mask, 255,255,255)
    contours,hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    res = cv2.bitwise_and(image, image, mask=mask)
    cv2.drawContours(res, contours, -1, (0,255,0), 3)


    cv2.imshow("Detected marker", marker)
    cv2.imshow("Erode and dilate", erdil)
    cv2.imshow("Mask", mask)
    cv2.imshow("Result", res)

    key = cv2.waitKey(1) & 0xFF
    rawCapture.truncate(0)
    if key == ord("q"):
        break
