import time
import cv2
import cv2.aruco as aruco
import numpy as np
import threading as T
import atexit
from picamera.array import PiRGBArray
from picamera import PiCamera
import sys

# Low res to get more frames, o(n) for pixel size
camera = PiCamera()
x_res = 320
camera.resolution = (x_res, 240)
camera.framerate = 32
camera.rotation = 180
# Should make less motion blur tm
camera.exposure_mode = 'sports'
print(camera.iso)
rawCapture = PiRGBArray(camera, size=(320, 240))
six_by_six = False
avg = []


# Allow the camera to warmup
time.sleep(0.1)

# Boundries for the detection
lower = np.array([50])
upper = np.array([255])
kernel = np.ones((5,5), np.uint8)

# Globals
filtered = None
stop_pls = False
aruco_and_middle = (-1, -1)


# The main tread will call this to get result
def get_result():
    return aruco_and_middle

# Make the x in the [0, 1] interval
def concat(raw):
    global x_res
    return raw / x_res


def main():
    global aruco_and_middle, stop_pls, filtered

    # Set aruco sizes and then load the dictionaries
    if six_by_six:
        aruco_dict = aruco.Dictionary_get(aruco.DICT_6X6_1000)
    else:
        aruco_dict = aruco.Dictionary_get(aruco.DICT_4X4_1000)
    parameters = aruco.DetectorParameters_create()

    # Keep running
    for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
        b = time.time()

        image = frame.array
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        corners,ids,rejectedImgPoints = aruco.detectMarkers(gray, aruco_dict, parameters=parameters)

        marker = aruco.drawDetectedMarkers(gray, corners)

        erdil = cv2.erode(gray, kernel, iterations=5)
        erdil = cv2.dilate(erdil, kernel, iterations=5)

        mask = cv2.inRange(erdil, lower, upper)
        mask = cv2.bitwise_not(mask)
        ret, thresh = cv2.threshold(mask, 255,255,255)
        contours,hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        res = cv2.bitwise_and(image, image, mask=mask)
        
        middle = -1
        middles = []
        if ids is None:
            for cnt in contours:
                x, y, w, h = cv2.boundingRect(cnt)
                middles.append(x+w/2.0)

        else:
            for corner in corners[0][0]:
                middles.append(corner[0])
        
        if (len(middles) > 0):
            middle = sum(middles)/len(middles)
        else:
            middle = -1

        
        if filtered is None:
            filtered = middle

        # Exponential moving average filter
        else:
            filtered = 0.7*middle + 0.3*filtered

        send = round(concat(filtered), 3)
        # Set the global variable
        aruco_and_middle = (ids, send)

        if ids is not None:
            # Used for statistics
            e = time.time()
            avg.append(e-b)


        # The image displays
        cv2.drawContours(res, contours, -1, (0,255,0), 3)
        cv2.imshow("Marker", marker)
        cv2.imshow("Result", res)

        key = cv2.waitKey(1) & 0xFF
        rawCapture.truncate(0)
        if key == ord("q"):
            print("Average aruco detection:", sum(avg)/len(avg))
            break


def stop():
    print("Aruco stop")
    raise SystemExit(0)

thread = T.Thread(target=main)
thread.start()
atexit.register(stop)

if __name__ == "__main__":
    try:
        pass
    except KeyboardInterrupt:
        
        stop()
