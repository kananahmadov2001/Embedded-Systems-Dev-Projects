from picar import PiCar
import time
import argparse

parser = argparse.ArgumentParser(description='Data for this program.')
parser.add_argument('--mock_car', action='store_true', help='If not present, run on car, otherwise mock hardware')
parser.add_argument('--tim', type=float, default=5, help='time to run (sec)')
parser.add_argument('--ADdelay', type=float, default=1, help='Time between samples of AD converter (sec)')
args = parser.parse_args()

car = PiCar(mock_car=args.mock_car)

car.set_motor(100)
time.sleep(1)

car.set_motor(50, forward=False)
time.sleep(1)

#car.set_motor(0)

start_time = time.time()
cur_time = start_time
msg_time = start_time

while cur_time - start_time < args.tim:
   cur_time = time.time()
   if (cur_time - msg_time > args.ADdelay):
      msg_time = cur_time

      dist = car.read_distance()
      print(f'Distance: {dist:.2f} cm')

      p0 = car.adc.read_adc(0)
      print(f'AD Reading: {p0}')
