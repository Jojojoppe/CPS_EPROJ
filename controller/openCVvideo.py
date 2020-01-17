#https://www.pyimagesearch.com/2015/03/30/accessing-the-raspberry-pi-camera-with-opencv-and-python/
"""
 pip install "picamera[array]"
"""
# color ranges: https://pysource.com/2019/02/15/detecting-colors-hsv-color-space-opencv-with-python/

import time
import cv2 as cv
import numpy as np
import threading as T
import atexit

import os
if os.uname()[4][:3]=="arm": # this is a pi
	from picamera.array import PiRGBArray
	from picamera import PiCamera
else:
	class _someClass:
		def truncate(self, i=0): pass

	def PiRGBArray(_,size): return _someClass()

	class _someClass3:
		array = np.array([[[0,0,0]]*480]*640)
	class _someClass2:
		def __init__(self): self.resolution=(1,1)
		def capture_continuous(self,a,format=0,use_video_port=0):
			while 1: yield _someClass3()

	def PiCamera():return _someClass2()







# ----- Tuning variables -----
# Upper and lower bounds for green
lower = np.array([50, 50, 50])
upper = np.array([255, 255, 255])
# Minimum screen percentage covered by rectangle
threshold = 0.005
#show frames
debug=True
#use threading
threading = True
# ----------------------------


# Initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 32
camera.rotation = 180
rawCapture = PiRGBArray(camera, size=(640, 480))
 
kernel = np.ones((5,5), np.uint8)

# Allow the camera to warmup
time.sleep(0.1)

result_value=(0,[])
stop_pls=False
generator = None
def get_bottles():
	#if debug: print("get_bottles called with", result_value)
	if threading: return result_value
	else:
		try:
			return next(generator)
		except StopIteration:
			print("picamera stopped for some reason")
			exit()
# Draw rectangle around the objects in the frame, and return x-coordinates in [0, 1] range.
def draw(frame, rectangles):
	# Return if no rectangles were found
	if len(rectangles) == 0: return (0, []),[]
	pixels = len(frame) * len(frame[0])

	size, x, y, w, h = rectangles[0]
	# Too small to be a bottle (probably no bottles in view)
	if size < pixels * threshold: return (0, []),[]
	
	# Iterate other rectangles
	result = [(size, x, y, w, h)]
	for i in range(1, len(rectangles)):
		size, x, y, w, h = rectangles[i]
		
		# Too small to be a bottle
		if size < pixels * threshold: break
		
		# Contained in the other rectangles => potential shadow
		if result[0][1] <= x <= result[0][1] + result[0][3]: continue
		if result[0][1] <= x + w <= result[0][1] + result[0][3]: continue
		
		# Add to the result
		result.append((size, x, y, w, h))

	# Feedback if too much is found. Possibly color range is too large.
	if debug:
		if len(result) > 2: print('finding more that 2 rectangles')
		# We draw at most 2 bottles	
		for i in range(min(2, len(result))):
			_, x, y, w, h = result[i]
			# Draw rectangle
			cv.rectangle(frame, (x, y), (x+w, y+h), (0,0,255), 2)

	# Get x-coordinates of the bottles in range [0, 1] to abstract screen size
	coordinates = []
	for i in range(min(2, len(result))):
		coordinates.append((result[i][1] + result[i][3] / 2) / len(frame[0]))
	return (min(2, len(result)), sorted(coordinates)),result[:min(2,len(result))]
def main():
	global stop_pls, result_value
	for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
		# Erode and dilate the image. Filters noise, and smoothens the image.
		frame = frame.array
		frame = cv.erode(frame, kernel, iterations=5)
		frame = cv.dilate(frame, kernel, iterations=5)

		# Create green mask for the image.
		hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
		mask = cv.inRange(hsv, lower, upper)

		# Green mask & draw contours in the image
		ret, thresh = cv.threshold(mask, 255,255,255)
		contours,hierarchy = cv.findContours(thresh, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
		if debug: 
			res = cv.bitwise_and(frame, frame, mask=mask)
			cv.drawContours(res, contours, -1, (0,255,0), 3)
		else:
			res = frame
		# Create & sort rectangles of the objects
		pq = []
		for cnt in contours:
			x, y, w, h = cv.boundingRect(cnt)
			pq.append((w * h, x, y, w, h))
		pq.sort(reverse=True)

		# Draw largest rectangles & find x-coordinates
		result_value,conts = draw(res, pq)
		if debug:
			pass				
			#print("result:",result_value)
		# Live feedback to the screen
		key=ord('x')
		if debug:
			cv.imshow('mask', mask)
			cv.imshow('res',res)
			key = cv.waitKey(1) & 0xFF
		# Clear the stream in preparation for the next frame
		rawCapture.truncate(0)
	 
		# Press q to break the loop
		if stop_pls or key == ord("q"):
			stop_pls=True
			break

def gen_main():
	global stop_pls, result_value
	for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
		# Erode and dilate the image. Filters noise, and smoothens the image.
		frame = frame.array
		frame = cv.erode(frame, kernel, iterations=5)
		frame = cv.dilate(frame, kernel, iterations=5)

		# Create green mask for the image.
		hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
		mask = cv.inRange(hsv, lower, upper)

		# Green mask & draw contours in the image
		ret, thresh = cv.threshold(mask, 255,255,255)
		contours,hierarchy = cv.findContours(thresh, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
		if debug: 
			res = cv.bitwise_and(frame, frame, mask=mask)
			cv.drawContours(res, contours, -1, (0,255,0), 3)
		else:
			res = frame
		# Create & sort rectangles of the objects
		pq = []
		for cnt in contours:
			x, y, w, h = cv.boundingRect(cnt)
			pq.append((w * h, x, y, w, h))
		pq.sort(reverse=True)

		# Draw largest rectangles & find x-coordinates
		result_value,conts = draw(res, pq)
		if debug:
			pass				
			#print("result:",result_value)
		# Live feedback to the screen
		key=ord('x')
		if debug:
			cv.imshow('mask', mask)
			cv.imshow('res',res)
			key = cv.waitKey(1) & 0xFF
		# Clear the stream in preparation for the next frame
		rawCapture.truncate(0)
		yield result_value 
		# Press q to break the loop
		if stop_pls or key == ord("q"):
			stop_pls=True
			return




if threading:
	def stop_thread(): stop_pls=True

	thread = T.Thread(target=main)
	thread.start()
	atexit.register(stop_thread)
else:
	generator = gen_main()


if __name__ == "__main__":

	if threading:
		try:
			while not stop_pls: print(get_bottles())
		except KeyboardInterrupt:
			stop_thread()
	else:
		try:
			while 1: print(next(generator))
		except KeyboardInterrupt:
			pass
		except StopIteration:
			pass

