#!/usr/bin/env python

from __future__ import print_function
import adddeps  # fix sys.path
import sys
import os
from os import path
import numpy as np
import pickle
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import opentuner
from opentuner import ConfigurationManipulator
from opentuner import IntegerParameter
from opentuner import EnumParameter
from opentuner import MeasurementInterface
from opentuner import Result
import argparse

parser = argparse.ArgumentParser(parents=opentuner.argparsers())
parser.add_argument('--input-size',
                    help='Input size to test with')
parser.add_argument('--type',
                    help='Which benchmark to try')

if len(sys.argv) < 8 or len(sys.argv) > 9 or sys.argv[1]!='--type' or sys.argv[3]!='--input-size' or sys.argv[5]!='--technique=ga-PX':
   print("Usage:  ./optimizer.py --type X --input-size M --technique=ga-PX --test-limit Y [--no-dups]")
   #print("Usage:  ./optimizer.py --type X --input-size M --technique=AUCBanditMetaTechniqueB --test-limit Y [--no-dups]") 
   sys.exit(0) 
	
type = sys.argv[2]
size = sys.argv[4]
mysize = float(size)

cmd = "./assign_cluster.py " + type 
os.system(cmd) #writes label of assigned cluster to cluster.txt

file = './cluster.txt'
f = open(file, 'r')
line = f.readline()
cluster = int(line.rstrip())

names = { #match cluster label with name
  0: "1st_cluster",
  1: "2nd_cluster",
  2: "3rd_cluster",
  3: "4th_cluster",
  4: "5th_cluster",
  5: "6th_cluster"
}

#load random forest model
filename = "./models/model_" + names[cluster] + ".sav"

model = pickle.load(open(filename, 'rb'))

default_pcms = np.array([0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0])

#load scaler
filename = "./scalers/std_" + names[cluster] + ".sav"
scaler = pickle.load(open(filename, 'rb'))

ready = path.exists('./pcm/' + type + '.txt')
if ready == False:
    cmd = "./find_averages_pcm.py " + type 
    os.system(cmd) #make type_def_large.txt file if not exists

#load values for the pcm related inputs of model
file = './pcm/' + type + '.txt'
f = open(file, 'r')
index = 0
line = f.readline()
while line:
    tokens = line.split('~')
    pcm = tokens[4].strip()
    default_pcms[index] = float(pcm)
    index +=1
    line = f.readline()
f.close()

params = np.array(['hibench.yarn.executor.cores', 'hibench.yarn.executor.num', 'spark.task.cpus', 'spark.shuffle.compress', 'spark.memory.fraction', 'spark.serializer', 'spark.scheduler.maxRegisteredResourcesWaitingTime', 'spark.default.parallelism', 'spark.sql.shuffle.partitions', 'spark.cleaner.periodicGC.interval', 'spark.io.compression.lz4.blockSize', 'spark.memory.storageFraction', 'spark.yarn.am.memory', 'spark.scheduler.revive.interval', 'spark.locality.wait.process', 'spark.shuffle.sort.bypassMergeThreshold', 'spark.shuffle.io.preferDirectBufs', 'spark.task.maxFailures', 'spark.files.openCostInBytes', 'spark.shuffle.file.buffer', 'spark.cleaner.referenceTracking.blocking', 'spark.kryoserializer.buffer.max', 'spark.executor.memory'])

class SparkParamsTuner(MeasurementInterface):

  def manipulator(self):
    """
    Define the search space by creating a
    ConfigurationManipulator
    """
    manipulator = ConfigurationManipulator()
    manipulator.add_parameter(EnumParameter('hibench.yarn.executor.cores', ['1', '4', '8', '16', '24', '48']))
    manipulator.add_parameter(EnumParameter('hibench.yarn.executor.num', ['1', '2', '3', '6', '12', '48']))
    manipulator.add_parameter(IntegerParameter('spark.task.cpus', 1, 4))
    manipulator.add_parameter(EnumParameter('spark.shuffle.compress', ['1', '0']))
    manipulator.add_parameter(EnumParameter('spark.memory.fraction', ['0.25', '0.4', '0.5', '0.6', '0.7', '0.8']))
    manipulator.add_parameter(EnumParameter('spark.serializer', ['0', '1']))
    manipulator.add_parameter(EnumParameter('spark.scheduler.maxRegisteredResourcesWaitingTime', ['10', '15', '25', '30', '40', '60']))
    manipulator.add_parameter(EnumParameter('spark.default.parallelism', ['8', '15', '25', '35', '50', '-1'])) #-1 represents default value of config and we need it
    manipulator.add_parameter(EnumParameter('spark.sql.shuffle.partitions', ['75', '100', '150', '200', '250', '400']))
    manipulator.add_parameter(EnumParameter('spark.cleaner.periodicGC.interval', ['5', '10', '15', '30', '35', '60']))
    manipulator.add_parameter(EnumParameter('spark.io.compression.lz4.blockSize', ['8', '16', '32', '40', '64', '80']))
    manipulator.add_parameter(EnumParameter('spark.memory.storageFraction', ['0.3', '0.35', '0.4', '0.5', '0.6', '0.7']))
    manipulator.add_parameter(EnumParameter('spark.yarn.am.memory', ['256', '400', '512', '750', '1000', '1500']))
    manipulator.add_parameter(EnumParameter('spark.scheduler.revive.interval', ['1000', '1500', '2000', '2500', '3000', '4000']))
    manipulator.add_parameter(EnumParameter('spark.locality.wait.process', ['1500', '2000', '2500', '3000', '4000', '6000']))
    manipulator.add_parameter(EnumParameter('spark.shuffle.sort.bypassMergeThreshold', ['75', '100', '150', '200', '250', '400']))
    manipulator.add_parameter(EnumParameter('spark.shuffle.io.preferDirectBufs', ['1', '0']))
    manipulator.add_parameter(EnumParameter('spark.task.maxFailures', ['1', '2', '3', '4', '6', '8']))
    manipulator.add_parameter(EnumParameter('spark.files.openCostInBytes', ['1000000', '2000000', '3500000', '4194304', '7000000', '9000000']))
    manipulator.add_parameter(EnumParameter('spark.shuffle.file.buffer', ['16', '28', '32', '45', '64', '80']))
    manipulator.add_parameter(EnumParameter('spark.cleaner.referenceTracking.blocking', ['1', '0']))
    manipulator.add_parameter(EnumParameter('spark.kryoserializer.buffer.max', ['24', '32', '50', '64', '90', '128']))
    manipulator.add_parameter(EnumParameter('spark.executor.memory', ['600', '1000', '2400', '4800', '9600', '19200', '54000', '108000']))	
    return manipulator

  def run(self, desired_result, input, limit):
    cfg = desired_result.configuration.data # a random parameter configuration
	
    X_test = np.zeros(33)
    for i in range(0, params.size): 
        X_test[i] = float(cfg[params[i]])
        if(i==2): #cpus used for each task cannot surpass total cores available
            if float(cfg['spark.task.cpus']) > float(cfg['hibench.yarn.executor.cores']):
                cpu = cfg['hibench.yarn.executor.cores']
                X_test[i] = float(cpu)
                cfg['hibench.yarn.executor.cores'] = cpu
        elif(i==7): #default in the machine of our experiments is 48
            if cfg['spark.default.parallelism']=='-1':
                X_test[i] = 48

    X_test[23] = mysize #the fixed datasize

    for k in range(24,33): #the fixed pcm metrics
        X_test[k] = default_pcms[k-24]

    #RandomForest inputs are 23 params, datasize and 9 pcm metrics
    X_test = X_test.reshape((1,33))
    scaled_X_test = scaler.transform(X_test) #scale test data
    prediction = model.predict(scaled_X_test) 

    #use predicted time as evaluation metric of the configuration
    return Result(time=prediction)

	
  def save_final_config(self, configuration):
    """called at the end of tuning"""
    print("Optimal parameter configuration written to file.json:", configuration.data)
    self.manipulator().save_to_file(configuration.data,
                                    './configs/' + type + '_' + size + '.json')

if __name__ == '__main__':
  args = parser.parse_args()
  SparkParamsTuner.main(args)
