# spark_tuning
ML-driven Automated Framework for Tuning Spark Applications - Diploma Thesis

In this thesis, we design a framework that tunes in an automated way Spark’s parameters, depending on the workload and the size of the input data. We locate the parameters with the greatest impact on the execution of the applications and we form a methodology to tune them accordingly so as to minimize the execution time. Specifically, we execute a
series of experiments to create our training dataset and then we perform a clustering of the different applications that we have selected to use for developing and testing the results, in order to split them into groups of similar ones. Afterwards, we make a representative regression model of each group/cluster that predicts accurately enough the execution time of an application input pair for a certain configuration. The models are fed to an optimization algorithm, which uses them for evaluating the different configuration vectors easily and quickly, and producing the optimal configuration. Finally, we integrate our solution into Spark, with the use of a wrapper script and we provide the user the chance to run a simple spark-submit command but actually executing the one with the optimal configuration.

Prerequisites: Python, OpenTuner, Docker. 

First run create_models.sh to create all the models of the Framework. 
Then make a docker image with hadoop and spark installed and use the -v flag to connect with the myreport file. 

Instead of a spark-submit command use the ./spark_submit.sh command to execute with optimal config. 
Run spark_submit.sh with flag --help to check how it is used
It runs the jar one time to collect low-level data, 
as long as they don't already exist, and then it executes the 
optimizer to find the optimal configuration for the given input 
data size. At last, it runs the jar with the optimal configuration
and saves it for future use.

Read the pdf for further info about the way the framework operates.
