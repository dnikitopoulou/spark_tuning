#!/bin/bash

clusters=("1st_cluster" "2nd_cluster" "3rd_cluster" "4th_cluster" "5th_cluster" "6th_cluster")

for i in {0..5} #create 6 models
do
	./make_model.py ${clusters[${i}]}
done
