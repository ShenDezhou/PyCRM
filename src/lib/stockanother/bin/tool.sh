#!/bin/bash
#coding=gb2312
# 一些常见的公共函数库



# 日志打印
function INFO() {
	now=`date "+%Y-%m-%d %H:%M:%S"`
	message=$1
	echo "$now [INFO]: $message"
}

function ERROR() {
	now=`date "+%Y-%m-%d %H:%M:%S"`
	message=$1
	echo "$now [ERROR]: $message"
}


# 文件备份，备份一个指定文件，加上当天的时间
function BACKUP() {
	file=$1;  TODAY=`date +%Y%m%d`
	if [ -f $file ]; then
		if [ -f $file.$TODAY ]; then
			rm -f $file.$TODAY
		fi
		mv $file $file.$TODAY
	fi
	INFO "backup $file to $file.$TODAY"
}

# 目录备份，备份一个指定目录，加上当天的时间
function BACKUPDIR() {
	dir=$1;  TODAY=`date +%Y%m%d`
	if [ -d $dir ]; then
		if [ -d $dir.$TODAY ]; then
			rm -rf $dir.$TODAY
		fi
		mv $dir $dir.$TODAY
	fi
	INFO "backup $dir to $dir.$TODAY"
}


#INFO "hello world"
