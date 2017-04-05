#INPUT:
#1.输入文件，格式：url\t*** 
#2.pattern.conf: 需要提取的pattern列表，每行一个pattern，如http://data.yule.sohu.com/star/data/[0-9]+/[0-9]+
#output:
#1.指定输出目录
#2.reduce的数量

#CURR_PATH=`cd $(dirname $0);pwd;`
#cd $CURR_PATH

diablo_host=$(bin/get_diablo_namenode.sh)

HADOOP_USER=web_tupu


patternConf=$1
outDir=${patternConf/_conf/}
outDir=$(basename $outDir)

rm -f conf/pattern.conf
cp $patternConf conf/pattern.conf

hadoop dfs -rmr /user/$HADOOP_USER/GetUrl/Pattern/pattern.conf
hadoop dfs -put $patternConf /user/$HADOOP_USER/GetUrl/Pattern/pattern.conf
hadoop dfs -rmr /user/$HADOOP_USER/GetUrl/$outDir


#-D dfs.socket.timeout=3600000 \
#-D dfs.datanode.socket.write.timeout=3600000 \

hadoop jar /usr/lib/hadoop-mapreduce/hadoop-streaming.jar  \
    -input  hdfs://$diablo_host/online/la/norm/url.in.offline/ \
    -output /user/$HADOOP_USER/GetUrl/$outDir \
    -numReduceTasks 1 \
    -mapper pattern_url_mapper.py -reducer pattern_url_reducer.py \
    -file bin/pattern_url_mapper.py -file conf/pattern.conf -file bin/pattern_url_reducer.py

rm -rf output/$outDir
hadoop dfs -get /user/$HADOOP_USER/GetUrl/$outDir ./output/
