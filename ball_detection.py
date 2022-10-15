from picamera.array import PiRGBArray
from picamera import PiCamera
import cv2
import time
import numpy as np
import imutils

defaultSpeed = 50
windowCenter = 320
centerBuffer = 10
pwmBound = float(50)
cameraBound = float(320)
kp = pwmBound / cameraBound
leftBound = int(windowCenter - centerBuffer)
rightBound = int(windowCenter + centerBuffer)
error = 0
ballPixel = 0

camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 15
rawCapture = PiRGBArray(camera, size = (640, 480))
fourcc = cv2.VideoWriter_fourcc(*'XVID')
vidOut = cv2.VideoWriter('video_output.avi', fourcc, 30, (640, 480))
time.sleep(0.1)

lower_yellow = np.array([10, 65, 90])
upper_yellow = np.array([40, 255, 255])

for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
	
	image = frame.array
	output = image.copy()
	hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
	
	mask = cv2.inRange(hsv, lower_yellow, upper_yellow)
	mask = cv2.erode(mask, None, iterations=2)
	mask = cv2.dilate(mask, None, iterations=2)
	output = cv2.bitwise_and(output, output, mask=mask)
	gray = cv2.cvtColor(output, cv2.COLOR_BGR2GRAY)
	circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 3, 500, minRadius = 10, maxRadius = 200, param1 = 100,  param2 = 60)
	ballPixel = 0
	
	if circles is not None:
		circles = np.round(circles[0, :]).astype("int")
		for (x, y, radius) in circles:
			cv2.circle(output, (x, y), radius, (0, 255, 0), 4)
			if radius > 10:	
				ballPixel = x
			else:
				ballPixel = 0
	
	vidOut.write(output)
	cv2.namedWindow("result")
	key = cv2.waitKey(1) & 0xFF
	rawCapture.truncate(0)
	
	if key == ord('q'):
		break

cv2.destroyAllWindows()
vidOut.release()
camera.close()