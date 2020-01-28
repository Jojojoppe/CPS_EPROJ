import time
import cv2
import cv2.aruco as aruco
import numpy as np
import threading as T
import atexit
from picamera.array import PiRGBArray
from picamera import PiCamera
import sys




camera = PiCamera()
x_res = 320
camera.resolution = (x_res, 240)
camera.framerate = 32
camera.rotation = 180
rawCapture = PiRGBArray(camera, size=(320, 240))


lower = np.array([50])
upper = np.array([255])
kernel = np.ones((5,5), np.uint8)

for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):

    image = frame.array
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    cv2.imshow("Result", gray)


    rawCapture.truncate(0)