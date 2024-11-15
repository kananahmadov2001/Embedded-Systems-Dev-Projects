from picamera2 import Picamera2
import cv2
import numpy as np
import math
import time
import argparse
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BOARD)
from picar import PiCar

freq = 50

lowerBound_dutycycle = -10
upperBound_dutycycle = 10

PWM_angle_ratio= -0.061

# using command line arguments for length of time to run (default 10 seconds), time between image captures (default 0.5 seconds) and a DEBUG variable (default False)

parser = argparse.ArgumentParser(description="Command Line Arguments")
parser.add_argument('--mock_car', action='store_true', help='If not present, run on car, otherwise mock hardware')
parser.add_argument('--tim', type=int, default=10, help='length of time to run (sec)')
parser.add_argument('--delay', type=float, default=0.5, help='time between image captures (sec)')
parser.add_argument('--delta', type=float, default=0.5, help='constant')
parser.add_argument('--debug', action='store_true', help="Enable debug mode")
args = parser.parse_args()

# Configure pin for output, then create PWM instance for pin w frequency and start
#GPIO.setup(PWM_pin, GPIO.OUT)
#pwm = GPIO.PWM(PWM_pin, freq)

def blue_object_angle(img, debug):

   hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
   # 1st set of values (105, 150, 150) form lower limits, the second the upper
   mask = cv2.inRange(hsv, (95, 150, 150), (132, 255, 255)) # blue range

   if debug:
      cv2.imwrite('mask.jpg', mask)

   mask_blur = cv2.blur(mask, (5,5))
   thresh = cv2.threshold(mask_blur, 100, 255, cv2.THRESH_BINARY)[1]
   if debug:
      cv2.imwrite('thresh.jpg', thresh)

   M = cv2.moments(thresh)
   #return M

   # if the object is not present, we have to return an angle of 360
   default_angle = 360

   # checking if the object is present with the center of mass interpretation
   if M["m00"] != 0:
      cX = int(M["m10"] / M["m00"])
      cY = int(M["m01"] / M["m00"])
      image = cv2.circle(img, (cX,cY), 5, (0,0,255), 2)  # red circle
      if debug:
         cv2.imwrite('filtered.jpg', image)

      # Find angle
      angle = math.atan((image.shape[0] - cY) / (cX - (image.shape[1]/2)))
      angle_in_degrees = angle*180/math.pi

      if debug:
         print(f"Angle from camera: {angle_in_degrees} ")

      return angle_in_degrees

   else:
      return default_angle

car = PiCar(mock_car=args.mock_car)

dutyCycle = 7.5

car.set_swivel_servo(dutyCycle)

time.sleep(1)

start_time = time.time()
cur_time = start_time
msg_time = start_time

camera = Picamera2()

dutyCycle1 = dutyCycle

while cur_time - start_time < args.tim:
    cur_time = time.time()
    if (cur_time - msg_time > args.delay):
        msg_time = cur_time

        # Take Image
        #camera = Picamera2()
        camera.start()
        array = camera.capture_array("main")
        array_bgr = cv2.cvtColor(array, cv2.COLOR_RGB2BGR)
        flip_image = cv2.flip(array_bgr,-1)

        # using the function from the problem 6 to determine the angle
        angle = blue_object_angle(flip_image,True)
        if args.debug:
            print(angle)
        print(f'delta:{args.delta}\t angle:{angle}\t pmw_AR:{PWM_angle_ratio}')

        # not moving the servo if the object is not present or if it requires the servo to move past its limited range of duty cycles
        if (angle == 360):
            dutyCycle1 = dutyCycle
            #pwm.ChangeDutyCycle(dutyCycle)
        elif (dutyCycle < lowerBound_dutycycle):
            dutyCycle1 = lowerBound_dutycycle
         #   pwm.ChangeDutyCycle(dutyCycle)
        elif (dutyCycle > upperBound_dutycycle):
            dutyCycle1 = upperBound_dutycycle
        #    pwm.ChangeDutyCycle(dutyCycle)
        else:
            dutyCycle1 = dutyCycle1 - args.delta * angle * PWM_angle_ratio

        car.set_swivel_servo(dutyCycle1)
