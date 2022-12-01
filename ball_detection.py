from picamera.array import PiRGBArray
from picamera import PiCamera
import cv2
import time
import imutils
import numpy as np
import gpiozero

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
image_width = 640
image_height = 480
center_image_x = image_width / 2
center_image_y = image_height / 2
minimum_area = 250
maximum_area = 100000
time.sleep(0.1)

lower_yellow = np.array([10, 65, 90])
upper_yellow = np.array([40, 255, 255])

for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
	
	image = frame.array
	output = image.copy()
	hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
	
	
 
robot = gpiozero.Robot(left=(22,27), right=(17,18))
forward_speed = 1.0
turn_speed = 0.8
 
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):

    image = frame.array
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    color_mask = cv2.inRange(hsv, lower_yellow, upper_yellow)
 
    image2, contours, hierarchy = cv2.findContours(color_mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
 
    object_area = 0
    object_x = 0
    object_y = 0

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
 
    for contour in contours:
        x, y, width, height = cv2.boundingRect(contour)
        found_area = width * height
        center_x = x + (width / 2)
        center_y = y + (height / 2)
        if object_area < found_area:
            object_area = found_area
            object_x = center_x
            object_y = center_y
    if object_area > 0:
        ball_location = [object_area, object_x, object_y]
    else:
        ball_location = None
 
    if ball_location:
        if (ball_location[0] > minimum_area) and (ball_location[0] < maximum_area):
            if ball_location[1] > (center_image_x + (image_width/3)):
                robot.right(turn_speed)
                print("Turning right")
            elif ball_location[1] < (center_image_x - (image_width/3)):
                robot.left(turn_speed)
                print("Turning left")
            else:
                robot.forward(forward_speed)
                print("Chasing ball :)")
        elif (ball_location[0] < minimum_area):
            robot.left(turn_speed)
            print("Tennis ball is too far away")
        else:
            robot.stop()
            print("Tennis ball too close, slowing down")
    else:
        robot.left(turn_speed)
        print("Still searching for ball")
 
    rawCapture.truncate(0)
