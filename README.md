# spark_tuning
ML-driven Automated Framework for Tuning Spark Applications

Prerequisites: Python, OpenTuner, Docker
First run create_models.sh to create all the models of the Framework 
Then make a docker image with hadoop and spark installed and use the -v flag to connect with the myreport file
Instead of a spark-submit command use the ./spark_submit.sh command to execute with optimal config
