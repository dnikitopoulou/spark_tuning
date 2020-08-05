#!/usr/bin/env python3

import sys
import os
import numpy as np

type = sys.argv[1]
titles = np.array(['AFREQ','L3MISS','L2MISS','L3HIT','L2HIT','READ','WRITE','PhysIPC%','TotalQPIout'])
list = [3,4,5,6,7,10,11,16,19]

file = './csvs/' + type + '.csv'
outfile = './pcm/' + type + '.txt'

for i in range(0, len(list)):
    cmd = "rm temp.txt"
    os.system(cmd)
    cmd = "awk -F ';' '{print $" + str(list[i]+3) + "}' " + file + " >> temp.txt"
    os.system(cmd)
    f = open('temp.txt', 'r') #temp.txt has one particular column at a time
    line = f.readline()
    line = f.readline()
    line = f.readline()
    sum = 0
    count = 0
    while line:
        sum += float(line.rstrip()) 
        count += 1
        line = f.readline()
    means = sum/count #mean is sum of all rows/number of rows
    f_out = open(outfile, "a")
    f_out.write(titles[i] + " ~~~~ " + str(means) + "\n") #construct the .txt file we need
    f_out.close()
