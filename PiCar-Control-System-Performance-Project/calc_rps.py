from scipy import signal
from scipy.fftpack import fft
import matplotlib
matplotlib.use('Pdf')
import matplotlib.pyplot as plt
import numpy as np
from mod9_func import movingAvg

fname   = input('Enter filename: ')
file    = open(fname, 'r')
data    = file.read().splitlines()  # split lines into an array 
MAXSIZE = len(data)
DEBUG   = False                     # For printing debug statements

time = [0]*MAXSIZE
ad_reading = [0]*MAXSIZE
difference_ad_reading = [0]*MAXSIZE
movingAVG_ad_reading = [0]*MAXSIZE
peak_transition = [0]*MAXSIZE

i=0
for dat in data:
    values   = dat.split()          # split on white space
    time[i]  = float(values[0])
    ad_reading[i] = float(values[1])

    if i == 0:
        difference_ad_reading[i] = 0
    else:
        difference_ad_reading[i] = ad_reading[i] - ad_reading[i-1]

    movingAVG_ad_reading[i] = float(movingAvg(difference_ad_reading,i,3,0))

    if DEBUG:
      print (f'{i}\t{time[i]}\t{ad_reading[i]}\t{difference_ad_reading[i]}\t{movingAVG_ad_reading[i]}\n')

    i = i + 1

threshold = np.abs((np.max(movingAVG_ad_reading[10:]) - np.min(movingAVG_ad_reading[10:]))/2)

change = 0
bool_transition = True

for i in range(1,len(movingAVG_ad_reading)):

    if (bool_transition == True and movingAVG_ad_reading[i] > 0.2 * threshold):
        change += 1
        bool_transition = False

    elif (bool_transition == False and movingAVG_ad_reading[i] < 0.2 * threshold):
        change += 1
        bool_transition = True
    i += 1

average_rps = int(change/4)/time[len(time)-5]
print(f'RPS: {average_rps:.3f}')
