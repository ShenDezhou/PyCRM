#!/bin/sh

#要检查的进程名
PROGRESS_NAME="run-monitor"

#-----------------------------------
# 函数: CheckProgress# 功能: 检查一个进程是否存在
# 参数: $1 --- 要检查的进程名称# 返回: 如果存在返回0, 否则返回1.
#---------------------------------------
CheckProgress(){  
# 检查输入的参数是否有效  
    if [ "$1" = "" ];  
    then
          return 1  
    fi    
#$PROCESS_NUM获取指定进程名的数目，为1返回0，表示正常，不为1返回1，表示有错误，需要重新启动  
    PROCESS_NUM=`ps -ef | grep "$1" | grep -v "grep" | wc -l`   
    if [ $PROCESS_NUM -eq 1 ];  
    then    
          return 0  
    else    
          return 1  
    fi
}
# 检查test实例是否已经存在
while [ 1 ] ; do 
    CheckProgress "$PROGRESS_NAME" 
    RET=$? 
    if [ $RET -eq 1 ]; 
    then
        echo "The progress:$PROGRESS_NAME is dead, I will start it right now!"
        #killall -9 $PROGRESS_NAME  
        exec python /root/wangjiang/gf-manager/glfs-web/run-monitor.py & 
    fi 
    sleep 1
    echo "sleep.."
done
