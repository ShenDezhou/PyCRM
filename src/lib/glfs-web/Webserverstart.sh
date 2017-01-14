#!/bin/bash
pidId=0
pidId=`ps -A |grep "run.py" |awk '{print $1}'`
#echo $pidId
if [ $pidId == '' ]; then
   $PWD/run.py >> Server.log &
   echo "Start Webserver Success"
else 
   kill -9 $pidId
   $PWD/run.py >> Server.log &
   echo "Start Webserver Success"
fi

