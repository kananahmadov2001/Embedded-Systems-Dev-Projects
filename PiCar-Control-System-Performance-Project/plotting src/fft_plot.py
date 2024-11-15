from scipy import signal
from scipy.fftpack import fft
import matplotlib
matplotlib.use('Agg')       # to avoid warnings if using ssh
import matplotlib.pyplot as plt
import numpy as np
import math
from mod9_func import movingAvg

T = 0.01 #time between samples

fname   = input('Enter filename: ')
file    = open(fname, 'r')
data    = file.read().splitlines()  # split lines into an array 
MAXSIZE = len(data)

power=0
while MAXSIZE >= int(math.pow(2,power+1)):
   power+=1

MAXSIZE = int(math.pow(2,power+1))
time = [0]*MAXSIZE
ad_reading = [0]*MAXSIZE
difference_ad_reading = [0]*MAXSIZE
movingAVG_ad_reading = [0]*MAXSIZE

i=0
for dat in data:
   if i in range(0,MAXSIZE-1):
      values = dat.split()
      time[i] = float(values[0])

      ad_reading[i] = float(values[1])

      if i == 0:
        difference_ad_reading[i] = 0
      else:
        difference_ad_reading[i] = ad_reading[i] - ad_reading[i-1]

   movingAVG_ad_reading[i] = float(movingAvg(difference_ad_reading,i,3,0))

   i+=1

AD_fft = fft(movingAVG_ad_reading)

freq = np.linspace(0, 1/(2*T), MAXSIZE//2)
plt.plot(freq, 2/MAXSIZE*abs(AD_fft[0:MAXSIZE//2]))
plt.grid(True)
plt.xlabel("freq - Hz")
plt.savefig("fft_objective1.png")
