import RPi.GPIO as GPIO
import Adafruit_MCP3008
from Adafruit_GPIO.GPIO import RPiGPIOAdapter as Adafruit_GPIO_Adapter
import argparse
import time
import numpy as np
from time import sleep
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
from mod9_func import movingAvg
from picamera2 import Picamera2
import cv2
import math
from picar import PiCar, configure

freq = 50

lowerBound_dutycycle = -10
upperBound_dutycycle = 10

PWM_angle_ratio = -0.0555

# using command line arguments
parser = argparse.ArgumentParser(description="Motor Command Line Arguments")
parser.add_argument('--mock_car', action='store_true', help='If not present, run on car, otherwise mock hardware')
parser.add_argument('--rps', type=float, default=5, help='rps')
parser.add_argument('--timRun', type=float, default=10, help='time to run (sec)')
parser.add_argument('--delay', type=float, default=0.5, help='time between image captures (sec)')
parser.add_argument('--delta', type=float, default=0.5, help='constant')
parser.add_argument('--timSamples', type=float, default=0.005, help='Time between samples of AD converter (msec)')
parser.add_argument('--timMotor', type=float, default=0.25, help='Time between calculating the motor speed (msec)')
parser.add_argument('--delayLoop', type=float, default=0, help='Time to wait to before starting the loop (sec)')
parser.add_argument('--delayMotor', type=float, default=1, help='Time to wait before turning the motor on (sec)')
parser.add_argument('--Kp', type=float, default=0.0, help='proportional control')
parser.add_argument('--Ki', type=float, default=0.0, help='integral control')
parser.add_argument('--Kd', type=float, default=0.0, help='derivative control')
parser.add_argument('--debug', action='store_true', help="Enable debug mode")
args = parser.parse_args()

def blue_object_angle(img, debug):

   hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
   # 1st set of values (105, 150, 150) form lower limits, the second the upper
   mask = cv2.inRange(hsv, (95, 100, 90), (120, 255, 255)) # blue range

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

      # fixing 'float division by zero' error
      if (cX - (image.shape[1]/2)) == 0:
         angle = 0

      else:
         # Find angle
         angle = math.atan(cY / (cX - (image.shape[1]/2)))

      angle_in_degrees = angle*180/math.pi

      if (angle_in_degrees > 0):
         angle_in_degrees = 90 - angle_in_degrees

      if (angle_in_degrees < 0):
         angle_in_degrees = -(90 - abs(angle_in_degrees))

      if debug:
         print(f"Angle from camera: {angle_in_degrees} ")

      return angle_in_degrees

   else:
      return default_angle


car = PiCar(mock_car=args.mock_car)

MAXSIZE = 1759
# 200 * args.timRun

time_array            = [0]*int(MAXSIZE)
AD_reading            = [0]*int(MAXSIZE)
RPSs                  = [0]*int(MAXSIZE)
transitions           = [0]*int(MAXSIZE)
difference_AD_reading = [0]*int(MAXSIZE)
movingAVG_AD_reading  = [0]*int(MAXSIZE)

angle = 360

freq                  = 50
lowerBound_dutycycle  = -10
upperBound_dutycycle  = 10

dutyCycle  = 0
dutyCycle1 = dutyCycle

car.set_swivel_servo(0)
car.set_nod_servo(2)
car.set_steer_servo(-2)
#car.set_motor(90)
#time.sleep(0.5)

#delta timing variables
start_time   = time.time()
cur_time     = start_time
msg_time     = start_time

msg_time_2   = start_time
msg_time_3   = start_time

index                     = 0
transition_index          = 0
threshold                 = 0
change                    = [0]*int(MAXSIZE)
Error                     = [0]*int(MAXSIZE)
DerivError                = [0]*int(MAXSIZE)
bool_transition           = True
transitions               = 0
temp                      = 0
SumError                  = 0
dummyVAR                  = 0
z                         = 0

close = False

camera = Picamera2()

while cur_time - start_time < args.timRun:
   cur_time = time.time()
   
   if (cur_time - msg_time_3 > args.delay):
         print(f'WORKINGGGG')
         msg_time_3 = cur_time

         camera.start()
         array = camera.capture_array("main")
         array_bgr = cv2.cvtColor(array, cv2.COLOR_RGB2BGR)
         #flip_image = cv2.flip(array_bgr,-1)

         # using the function from the problem 6 to determine the angle
         angle = blue_object_angle(array_bgr,True)
         if args.debug:
            print(angle)

         print(f'delta:{args.delta}\t angle:{angle}\t dutyCycle:{dutyCycle1}')

         # not moving the servo if the object is not present or if it requires the servo to move past its limited range of duty cycle
         if angle != 360:
            dutyCycle1 = dutyCycle1 + args.delta * angle * PWM_angle_ratio

            # dutyCycle1 = 2 * (dutyCycle1 - 7.5)

            if dutyCycle1 < -10:
               dutyCycle1 = lowerBound_dutycycle

            elif dutyCycle1 > 10:
               dutyCycle1 = upperBound_dutycycle

            #dutyCycle1 = (2 * dutyCycle1) - 7.5

            car.set_steer_servo(dutyCycle1)

            distance = car.read_distance()
            print(f'Distance: {distance:.2f} cm')

            if (distance < 40):
               print('DISTANCEEEEEEEEEEEEEEEEEEEEEEEEE')
               car.set_motor(0,forward=False)
               close = True


            elif abs(angle) < 7.5:
               car.set_steer_servo(0)

            else:
               dutyCycle1 = dutyCycle1 - 0.55*args.delta * angle * PWM_angle_ratio
               car.set_steer_servo(dutyCycle1)
               #car.set_motor(10)
         else:
            print(f'I DONT SEE A BLUE OBJECT')
   
   if (cur_time - msg_time > args.timSamples):
      msg_time = cur_time

      time_array[index] = cur_time - start_time
      #print(f'{time_array[index]}')
      AD_reading[index] = car.adc.read_adc(0)
      print(f'AD Readings: {AD_reading[index]}')

      if(cur_time - start_time >= args.delayMotor):

         if z == 0:
            car.set_motor(100)
            z=1

      # to calculate the RPS we need the difference in AD_reading, moving average of those differences, and the peak transitions
      if AD_reading[index] > 250 and AD_reading[index] < 650:

         if index > 0:
            print(f'index: {index}')
            difference_AD_reading[index] = AD_reading[index] - AD_reading[index-1]
            if index > 2:
               movingAVG_AD_reading[index] = float(movingAvg(difference_AD_reading,index,3,0))
               print(f'movingAVG: {movingAVG_AD_reading[index]}')
               if index - 100 > 0:
                  threshold = np.abs((np.max(movingAVG_AD_reading[index-100:index]) - np.min(movingAVG_AD_reading[index-100:index]))/2)
            else:
               movingAVG_AD_reading[index] = 0
               threshold = 0
         else:
            difference_AD_reading[index] = 0

      if (bool_transition == True and movingAVG_AD_reading[index] > 0.5 * threshold and index > temp + 4):
         change[index] = 1
         bool_transition = False
         temp = index
         #transitions += 1

      elif (bool_transition == False and movingAVG_AD_reading[index] < - 0.5 * threshold and index > temp + 4):
         change[index] = 1
         bool_transition = True
         temp = index
         #transitions += 1

      print(f'change: {change[index]}')

      if RPSs[index-1] > 0:
         RPSs[index] = RPSs[index-1]

      if(cur_time - msg_time_2 > args.timMotor):
        msg_time_2 = cur_time
        transition_index = index
        transitions = 0
        while(transitions < 5 and transition_index > 0):
           if change[transition_index] != 0:
              transitions += 1
              if transitions == 1:
                 first_transition_time = time_array[transition_index]
              elif transitions == 5:
                 fifth_transition_time = time_array[transition_index]

                 RPSs[index] = 1/(first_transition_time - fifth_transition_time)

                 if RPSs[index] > 10:
                    RPSs[index] = RPSs[index-1]

                 Error[index] = args.rps - RPSs[index]
                 dummyVAR += 1

                 if dummyVAR > 1:
                    DerivError[index] = Error[index] - Error[index-1]
                 SumError += Error[index]

           transition_index -= 1

      if args.debug:
        print(f'Time: {time_array[index]:.2f}\t RPSs: {RPSs[index]:.8f}\n')

      new_pwm = args.rps*(1/0.0802) + args.Kp*Error[index] + args.Ki*SumError + args.Kd*DerivError[index]
      print(f'pwm: {new_pwm}')

      #index += 1
      if(new_pwm < 0):
        new_pwm = 0
      if(new_pwm > 100):
        new_pwm = 100

      if close == False:
         car.set_motor(new_pwm)
         print(f'far away')
      elif close == True and angle != 360:
         car.set_motor(0)
         print(f'close to object')

      index +=1


# Writing to a file
input_txt = "car_"+str(args.rps)+".txt"

with open(input_txt,'w') as f:
    for i in range(0,len(time_array)-1):
        f.write(f'{time_array[i]:.4f}\t{AD_reading[i]}\t{RPSs[i]:.3f}\n')

GPIO.cleanup()
