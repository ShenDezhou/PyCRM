#!/bin/bash
#coding=gb2312
# һЩ�����Ĺ���������



# ��־��ӡ
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


# �ļ����ݣ�����һ��ָ���ļ������ϵ����ʱ��
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

# Ŀ¼���ݣ�����һ��ָ��Ŀ¼�����ϵ����ʱ��
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
