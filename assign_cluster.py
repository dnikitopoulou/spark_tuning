#!/usr/bin/env python3

import sys
import os
import numpy as np
from scipy.stats.mstats import gmean
from tslearn.utils import to_time_series_dataset
from tslearn.clustering import TimeSeriesKMeans
from tslearn.preprocessing import TimeSeriesResampler
import pickle

list = ('3','4','5','6','7','10','11','16','19') #metric indices in pcm file

bench = sys.argv[1] #takes benchmark as input

size = 2000 #resampling size

cmd = "rm cluster.txt"
os.system(cmd)

f = open('./csvs/' + bench + '.csv', 'r')
line = f.readline()
line = f.readline()
line = f.readline()
t = []
while line:
    pcms = []
    tokens = line.split(';')
    for j in range(2,34):
        if str(j-2) not in list:
            continue
        #if tokens[j]!='0':
        if float(tokens[j])>0:
            pcms.append(float(tokens[j])) #take all pcm values of the same time slot
    mean = gmean(pcms) #calculate their geometric mean
    t.append(mean) #hold representative value(geomean) of all metrics
    line = f.readline()
f.close()

#construct the new resampled signal of the current benchmark
formatted_dataset_test = to_time_series_dataset(t) 
formatted_dataset_test = TimeSeriesResampler(sz=size).fit_transform(formatted_dataset_test)

# load the SOFTDTW k-means model in order to be used for predicting the new signals' cluster
filename = 'clustering_model_1.sav'
sdtw_km = pickle.load(open(filename, 'rb'))

X_test = formatted_dataset_test
label = sdtw_km.predict(X_test) #this is the label of the cluster this benchmark belongs to

cmd = "echo " + str(label[0]) + " >> cluster.txt" #write it in file so that other programs can read it
os.system(cmd)
