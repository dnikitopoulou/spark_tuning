# spark_tuning
ML-driven Automated Framework for Tuning Spark Applications

Prerequisites: Python, OpenTuner, Docker
First run create_models.sh to create all the models of the Framework 
Then make a docker image with hadoop and spark installed and use the -v flag to connect with the myreport file

Instead of a spark-submit command use the ./spark_submit.sh command to execute with optimal config. 
Run spark_submit.sh with flag --help to check how it is used
It runs the jar one time to collect low-level data, 
as long as they don't already exist, and then it executes the 
optimizer to find the optimal configuration for the given input 
data size. At last, it runs the jar with the optimal configuration
and saves it for future use.

Read the pdf for further info about the way the framework operates.
