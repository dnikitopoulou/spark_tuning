#!/usr/bin/env python

import sys
import os
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
import pickle

type = sys.argv[1] #take cluster_id as input, eg 1st_cluster
#load features and outputs tables
X_train = pd.read_csv('./feature_matrices/' + type + '.csv',header=0)
y_train = pd.read_csv('./response_vectors/' + type + '.csv',header=0)

#scale data
scaler = StandardScaler() 
scaled_X_train = scaler.fit_transform(X_train)

#save scaler for later use
filename = './scalers/std_' + type + '.sav'
pickle.dump(scaler, open(filename, 'wb'))

# random forest
reg = RandomForestRegressor(random_state=42, max_depth=40, n_estimators=1000)
reg.fit(scaled_X_train, y_train.values.ravel())

#save random forest model for later use
filename = './models/model_' + type + '.sav'
pickle.dump(reg, open(filename, 'wb'))

