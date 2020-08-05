#!/bin/bash

if [ "$1" = "--help" ] ;
then
	echo "Usage: sudo ./spark_submit.sh --class X jarName hdfsPath ..."
	echo "with input passed to hdfs in path /Hibench/ProgName/Input"
	exit
fi

if [ ! "$1" = "--class" ] ;
then
	echo "Wrong arguments"
	echo "run './spark_submit.sh --help' for instructions"
	exit
fi


name=$(echo $2 | awk -F'.' '{print $NF}')
echo ${name}

temp=$(echo $@ | awk -F'//' '{print $2}')
echo ${temp}

bench=$(echo $temp | awk -F'/' '{print $3}')
echo ${bench}

dirsize="Input"
if [ "$name" = "ScalaSparkSQLBench" ] ;
then
	dirsize="Output"
	name=$4
	bench=${name:5}
fi

if [ "$bench" = "Join" ] ;
then
	dirsize="Input"
fi

echo ${name}
echo ${bench}

path=$(cat benchmarks.txt | grep $bench)
echo ${path}

WORKLOAD=/HiBench/bin/workloads/${path,,}
echo ${WORKLOAD}

if [ "$dirsize" = "Output" ] ;
then
	docker exec -it exper $WORKLOAD/spark/run.sh default
	rm store.sh
	echo "#!/bin/bash" >> store.sh
	echo "" >> store.sh
	echo "hdfs dfs -rm -r /HiBench/${bench}/TempOutp" >> store.sh
	echo "hdfs dfs -cp /HiBench/${bench}/Output /HiBench/${bench}/TempOutp" >> store.sh
	chmod +x store.sh
	docker cp ./store.sh exper:/HiBench/store.sh
	docker exec -it exper /HiBench/store.sh
fi

FILE=./csvs/${name}.csv
if test ! -f "$FILE"; then
	echo "$FILE does not exist"
	docker cp ./spark_def exper:/HiBench/conf/spark.conf

	if [ ! -z "$path" ];
	then
		echo "is benchmark and we'll make large data"
	
		sed -i "s/.*scale.prof.*/hibench.scale.profile	large/" ./hibench.conf
		docker cp ./hibench.conf exper:/HiBench/conf/hibench.conf

		rm store.sh
		echo "#!/bin/bash" >> store.sh
		echo "" >> store.sh
		echo "hdfs dfs -rm -r /HiBench/${bench}/TempInp" >> store.sh
		echo "hdfs dfs -cp /HiBench/${bench}/Input /HiBench/${bench}/TempInp" >> store.sh
		chmod +x store.sh 
		docker cp ./store.sh exper:/HiBench/store.sh
		docker exec -it exper /HiBench/store.sh
	
		docker exec -it exper ${WORKLOAD}/prepare/prepare.sh

                result=$?
                if [ $result -ne 0 ]
                then
                   echo "ERROR: ${benchmark} prepare failed!"
                   exit $result
                fi
		
		#run default 
	
		modprobe msr
		../../../pcm.x 0.1 -r -csv=output.csv 1>&- 2>&- & #Background process
		docker exec -it exper $WORKLOAD/spark/run.sh default

		result=$?
		if [ $result -ne 0 ]
		then
			echo -e "ERROR: ${benchmark}/spark failed to run successfully."
			exit $result
		fi

		killall -9 pcm.x
		mv output.csv csvs
		mv ./csvs/output.csv "./csvs/${name}.csv" #Move results to output
	
		rm store.sh
		echo "#!/bin/bash" >> store.sh
		echo "" >> store.sh
		echo "hdfs dfs -rm -r /HiBench/${bench}/Input" >> store.sh
		echo "hdfs dfs -cp /HiBench/${bench}/TempInp /HiBench/${bench}/Input" >> store.sh
		chmod +x store.sh

		docker cp ./store.sh exper:/HiBench/store.sh
		docker exec -it exper /HiBench/store.sh
	else
		rm run.sh
		echo "#!/bin/bash" >> run.sh
		echo "" >> run.sh
		echo "hdfs dfs -rm -r /HiBench/${bench}/Output" >> run.sh
		echo "/usr/local/spark-1.6.0-bin-hadoop2.6/bin/spark-submit --properties-file /HiBench/conf/spark.conf --master yarn-client $@/" >> run.sh
		chmod +x run.sh
		docker cp ./run.sh exper:/HiBench/run.sh
		
		#run default 
	
		modprobe msr
		../../../pcm.x 0.1 -r -csv=output.csv 1>&- 2>&- & #Background process
		docker exec -it exper /HiBench/run.sh
		
		killall -9 pcm.x
		mv output.csv csvs
		mv ./csvs/output.csv "./csvs/${name}.csv" #Move results to output
		
	fi
fi

if [ "$dirsize" = "Output" ] ;
then
	rm store.sh
	echo "#!/bin/bash" >> store.sh
	echo "" >> store.sh
	echo "hdfs dfs -rm -r /HiBench/${bench}/Output" >> store.sh
	echo "hdfs dfs -cp /HiBench/${bench}/TempOutp /HiBench/${bench}/Output" >> store.sh
	chmod +x store.sh
        docker cp ./store.sh exper:/HiBench/store.sh
        docker exec -it exper /HiBench/store.sh
fi

rm ./myreport/size.txt
rm find_size.sh
echo "#!/bin/bash" >> find_size.sh
echo "" >> find_size.sh
rm /HiBench/docs/size.txt
echo "hdfs dfs -du -s hdfs://sandbox:9000/HiBench/${bench}/${dirsize} >> /HiBench/docs/size.txt" >> find_size.sh
chmod +x find_size.sh
docker cp ./find_size.sh exper:/HiBench/find_size.sh
docker exec -it exper /HiBench/find_size.sh

M=$(cat ./myreport/size.txt | awk -F' ' '{print $1}')
echo $M

FILE=./configs/${name}_${M}.json
if test ! -f "$FILE"; then
	echo "$FILE does not exist"
	./optimizer.py --type ${name} --input-size ${M} --technique=ga-PX --test-limit 299 --no-dups
	#./optimizer.py --type ${name} --input-size ${M} --technique=AUCBanditMetaTechniqueB --test-limit 299 --no-dups
fi

./make_spark_config.py ${name}_${M}.json 

if [ ! -z "$path" ];
then
	echo "is benchmark"

	docker cp ./spark_config exper:/HiBench/conf/spark.conf
	docker exec -it exper $WORKLOAD/spark/run.sh config

        result=$?
        if [ $result -ne 0 ]
        then
            echo -e "ERROR: ${benchmark}/spark failed to run successfully."
            exit $result
        fi
else
	sed -i 's/hibench.yarn.executor.cores/spark.executor.cores/g' ./spark_config
	sed -i 's/hibench.yarn.executor.num/spark.executor.instances/g' ./spark_config 
	docker cp ./spark_config exper:/HiBench/conf/spark.conf

	echo "is not benchmark"
	rm run.sh 
	echo "#!/bin/bash" >> run.sh
	echo "" >> run.sh
	echo "hdfs dfs -rm -r /HiBench/${bench}/Output" >> run.sh
	echo "/usr/local/spark-1.6.0-bin-hadoop2.6/bin/spark-submit --properties-file /HiBench/conf/spark.conf --master yarn-client $@/" >> run.sh
	chmod +x run.sh
        docker cp ./run.sh exper:/HiBench/run.sh	
	docker exec -it exper /HiBench/run.sh
fi

#hdfs cp to palio input	
		

