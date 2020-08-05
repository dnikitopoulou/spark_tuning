#!/usr/bin/env python

import json
import sys
import os

myfile = sys.argv[1]

f = open('./configs/' + myfile,)
params = json.load(f) 

cmd = "rm spark_config"
os.system(cmd)

cmd = "cp spark_temp spark_config"
os.system(cmd)

f_out = open("./spark_config", "a")

for param in params:
    val = params[param]
    myval = str(val)
    if param=='spark.shuffle.compress' or param=='spark.shuffle.io.preferDirectBufs' or param=='spark.cleaner.referenceTracking.blocking':
        if myval == '0':
            myval = 'false'
        else:
            myval = 'true'
    elif param=='spark.serializer':
        if myval == '0':
            continue
        else:
            myval = 'org.apache.spark.serializer.KryoSerializer'
    elif param=='spark.scheduler.maxRegisteredResourcesWaitingTime':
        myval = myval + 's'
    elif param=='spark.cleaner.periodicGC.interval':
        myval = myval + 'min'
    elif param == 'spark.io.compression.lz4.blockSize' or param == 'spark.shuffle.file.buffer':
        myval = myval + 'k'
    elif param == 'spark.yarn.am.memory' or param == 'spark.kryoserializer.buffer.max' or param == 'spark.executor.memory':
        myval = myval + 'm'
    elif param == 'spark.scheduler.revive.interval' or param =='spark.locality.wait.process':
        myval = myval + 'ms'
    elif param == 'spark.default.parallelism' and myval == '-1':
        continue
    #print(str(param) + ' ' + myval)
    f_out.write(param + '   ' + myval + '\n')

