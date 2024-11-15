from picar import PiCar
import time
import argparse

parser = argparse.ArgumentParser(description='Data for this program.')
parser.add_argument('--mock_car', action='store_true', help='If not present, run on car, otherwise mock hardware')
parser.add_argument('--tim', type=float, default=10, help='time to run (sec)')
parser.add_argument('--ADdelay', type=float, default=1, help='Time between samples of AD converter (sec)')
args = parser.parse_args()

car = PiCar(mock_car=args.mock_car)

start_time = time.time()
cur_time = start_time
msg_time = start_time

while cur_time - start_time < args.tim:
   cur_time = time.time()
   if (cur_time - msg_time > args.ADdelay):
      msg_time = cur_time

      distance = car.read_distance()
      print(f'Distance: {distance:.2f} cm')

      if (distance >= 50):
         car.set_motor(0)

      elif (distance < 10):
         car.set_motor(0)

      elif (distance >= 10 and distance < 15):
         car.set_motor(10)
      elif (distance >= 15 and distance < 20):
         car.set_motor(20)
      elif (distance >= 20 and distance < 25):
         car.set_motor(30)
      elif (distance >= 25 and distance < 30):
         car.set_motor(40)
      elif (distance >= 30 and distance < 35):
         car.set_motor(50)
      elif (distance >= 35 and distance < 40):
         car.set_motor(60)
      elif (distance >= 40 and distance < 45):
         car.set_motor(70)
      elif (distance >= 45 and distance < 50):
         car.set_motor(80)
