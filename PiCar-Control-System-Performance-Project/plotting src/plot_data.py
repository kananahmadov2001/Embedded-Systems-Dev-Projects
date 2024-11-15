import matplotlib
matplotlib.use('Pdf')               # We are just printing
import matplotlib.pyplot as plt
import numpy as np

fname   = input('Enter filename: ')
file    = open(fname, 'r')
data    = file.read().splitlines()  # split lines into an array 
MAXSIZE = len(data)
DEBUG   = False                     # For printing debug statements

time    = [0]*MAXSIZE
RPS     = [0]*MAXSIZE

i=0
for dat in data:
    values   = dat.split()          # split on white space
    time[i]  = float(values[0])     # first item in file is time
    RPS[i] = float(values[2])       # second is the value

    if DEBUG: print (f'{i}\t{time[i]}\t{RPS[i]}')
    i = i + 1


#max_val = max(RPS)
#print(f'peak RPS: {max_val}')

#get tick marks for the x axis, in 4 regions
xmarks = np.linspace(time[0], time[MAXSIZE - 1], 5) 
plt.xticks(xmarks)

plt.plot(time, RPS)
plt.grid()                          # show the grid
plt.xlabel('time - sec')
plt.ylabel('velocity - rev/sec')
plt.savefig('plot_objective3.png')
