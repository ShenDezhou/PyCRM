
HOST="master001.diablo.hadoop.nm.ted:50070"
HOSTS="master001.diablo.hadoop.nm.ted:50070 master002.diablo.hadoop.nm.ted:50070"

for host in $HOSTS
do
    RESULT=`curl -s "http://$host/jmx?qry=Hadoop:service=NameNode,name=NameNodeStatus"`
    if [[ $RESULT =~ "active" ]];then
        HOST=$host
    fi
done

echo ${HOST/50070/8020}

