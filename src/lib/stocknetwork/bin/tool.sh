#!/bin/bash
#coding=gb2312

# ��ǰʱ�䣬���ڼ�¼��־��
function now() {
	echo $(date "+%Y-%m-%d %H:%M:%S")
}

# ��ǰʱ�䣬���ڼ�¼��־��
function nowStr() {
	echo $(date "+%Y%m%d%H%M")
}

# ��ǰʱ�䣬���ڼ�¼��־��
function todayStr() {
	echo $(date "+%Y%m%d")
}

# ��ǰʱ�䣬���ڼ�¼��־��
function today() {
	echo $(date "+%Y-%m-%d")
}

# ��ӡ��־
function LOG() {
    	now=`date +"%Y-%m-%d %H:%M:%S"`
	echo $now" "$1
}

function INFO() {
    	now=`date +"%Y-%m-%d %H:%M:%S"`
	echo $now" [INFO] "$1
}

function ERROR() {
    	now=`date +"%Y-%m-%d %H:%M:%S"`
	echo $now" [ERROR] "$1
}


# �ж��ļ��Ƿ��ǽ������ɵ�
function isFileTodayCreate() {
	file=$1
	fileCreateDate=$(ls -l --time-style=long-iso $file | awk '{print $6}')
	today=$(today)
	if [ "$fileCreateDate" = "$today" ]; then
		echo "true"
	else
		echo "false"
	fi
}


# �ж��ļ��Ƿ񹻴�
function isFileSizeEnough() {
	file=$1;  sizeThreshold=$2
	fileCreateDate=$(ls -l --time-style=long-iso $file | awk '{print $5}')
	if [ $fileCreateDate -ge $sizeThreshold ]; then
		echo "true"
	else
		echo "false"
	fi
}




# �����ļ�
function backupFile() {
    today=$(date +%Y%m%d)
    srcFile=$1;
	destPath="./history"
	if [ $# -gt 1 ]; then
		destPath=$2
	fi


    if [ ! -f $srcFile ]; then
         echo "$srcFile is not exist;"
        return 0
    fi
    destFile=${destPath}/$(basename $srcFile)".$today"
    rm -f $destFile; cp -f $srcFile $destFile
    echo "baskup $srcFile into $destFile done."
}


# ���ļ�ת��һ��
function trans2line() {
    input=$1
    awk 'BEGIN{ line = ""} {
        gsub(/\n\r/, "", $0)
        line = line "" $0
    } END {
        print line
    }' $input
}


# ���ͱ����ʼ�
# arg1: report project name
# arg2: report message
function sendReportMail() {
	reportProj="$1";  message="$2"
	echo -e "<html><body><p><h1><font color=\"red\">$message</font></h1></p></body></html>" > /tmp/report.html
    	/usr/bin/sogou-mds-syncfile -m $reportProj -l /tmp/report.html
}




# ��ӡһ��Ŀ¼�¸����ļ���״̬��Ϣ
function getFileInfoOfDirectory() {
        directory=$1;
        listInfo=$(ls -l $directory | awk '{print $0"<br>"}')
        echo  $listInfo
}



function copy_file() {
	srcPath=$1;  destPath=$2;  fileName=$3;
	
	if [ ! -d $destPath ]; then
		mkdir -p $destPath
	fi
	
	srcFile=$srcPath/$fileName
	destFile=$destPath/$fileName
	
	srcFileLine=$(cat $srcFile | wc -l)
	if [ $srcFileLine -le 1 ]; then
		echo "$srcFileLine is too small"
		return 1
	fi

	if [ -f $destFile ]; then
		rm -f $destFile.bak;  mv $destFile $destFile.bak
	fi

	cp $srcFile $destFile
	echo "copy $srcFile to $destFile done."
}


