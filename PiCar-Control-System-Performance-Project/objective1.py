import RPi.GPIO as GPIO
import Adafruit_MCP3008
from Adafruit_GPIO.GPIO import RPiGPIOAdapter as Adafruit_GPIO_Adapter
from picar import PiCar
import argparse
import time
import numpy as np
from time import sleep
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
from mod9_func import movingAvg

# command line arguments
parser = argparse.ArgumentParser(description="Motor Command Line Arguments")
parser.add_argument('--mock_car', action='store_true', help='If not present, run on car, otherwise mock hardware')
parser.add_argument('--rps', type=float, default=5, help='rps')
parser.add_argument('--timRun', type=float, default=10, help='time to run (sec)')
parser.add_argument('--timSamples', type=float, default=0.005, help='Time between samples of AD converter (msec)')
parser.add_argument('--timMotor', type=float, default=0.25, help='Time between calculating the motor speed (msec)')
parser.add_argument('--delayLoop', type=float, default=0, help='Time to wait to before starting the loop (sec)')
parser.add_argument('--delayMotor', type=float, default=1, help='Time to wait before turning the motor on (sec)')
parser.add_argument('--Kp', type=float, default=0.0, help='proportional control')
parser.add_argument('--Ki', type=float, default=0.0, help='integral control')
parser.add_argument('--Kd', type=float, default=0.0, help='derivative control')
parser.add_argument('--debug', action='store_true', help="Enable debug mode")
args = parser.parse_args()

car = PiCar(mock_car=args.mock_car)

# storing the collected data in arrays
MAXSIZE = 800
MAXSIZE = 2000
# in the future, just do 200 * args.tim

time_array = [0]*int(MAXSIZE)

AD_reading = [0]*int(MAXSIZE)
RPSs = [0]*int(MAXSIZE)
transitions = [0]*int(MAXSIZE)

difference_AD_reading = [0]*int(MAXSIZE)
movingAVG_AD_reading = [0]*int(MAXSIZE)

# delta timing
start_time = time.time()
cur_time = start_time
msg_time = start_time

msg_time_2 = start_time

index = 0
transition_index = 0
threshold = 0
change = [0]*int(MAXSIZE)
Error = [0]*int(MAXSIZE)
DerivError = [0]*int(MAXSIZE)
bool_transition = True
transitions = 0
temp = 0
SumError = 0
dummyVAR = 0
z=0
while cur_time - start_time < args.timRun:
   cur_time = time.time()
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
      if AD_reading[index] > 150 and AD_reading[index] < 650:

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

      #index += 1
      if(new_pwm < 0):
        new_pwm = 0
      if(new_pwm > 100):
        new_pwm = 100

      car.set_motor(new_pwm)

      index +=1


# Writing to a file
with open('car_noload_5rps.txt','w') as f:
    for i in range(0,len(time_array)-1):
        f.write(f'{time_array[i]:.4f}\t{AD_reading[i]}\t{RPSs[i]:.3f}\n')

GPIO.cleanup()
