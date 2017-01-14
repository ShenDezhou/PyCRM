#!/bin/bash
pidId=0
pidId=`ps -A |grep "run-monitor" |awk '{print $1}'`
#echo $pidId
if [ $pidId == '' ]; then
   $PWD/run-monitor.py >> monitor.log &
   echo "Start Monitor Success"
else 
   kill -9 $pidId
   $PWD/run-monitor.py >> monitor.log &
   echo "Start Monitor Success"
fi

