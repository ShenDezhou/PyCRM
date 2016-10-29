#!/bin/bash
#100000,200,12341234,4300303
#*************************
#100000,200*200/1,2*2
oldIFS=$IFS
IFS=','
temp0=$(mktemp -t domath.XXXXXX)
temp1=$(mktemp -t domath.XXXXXX)
temp2=$(mktemp -t domath.XXXXXX)
temp3=$(mktemp -t domath.XXXXXX)
temp4=$(mktemp -t domath.XXXXXX)
cut -f 1 -d , $1 >> $temp0
cut -f 6 -d , $1 >> $temp1
cut -f 7 -d , $1 >> $temp2

cut -f 6,7 -d , $1 | while read np pp; do
echo "scale=4;($pp - $np)/$np*100.0"|bc >> $temp3;
done

paste -d , $temp0 $temp1 $temp2 $temp3 >> $temp4

sum=0  
data=`cut -f 2 -d , $1`  
for i in $data  
do 
    sum=$(($sum+$i))  
done
now=$(date +%Y-%m-%d);
line=
line+=$now
line+=','
line+=$sum
echo $line >> 'cloudindex.txt'

read astock<"astock.txt"
read sstock<"sstock.txt"
read rstock<"rstock.txt"
stock+=$astock+$sstock+$rstock

buy=$(mktemp buy.XXXXXX)
sort -r -n -k 4,2 -t , $temp4 >> $buy
read html< "recommend-tpl-ann.html"
temp5=$(mktemp -t domath.XXXXXX)
head -n 3 $buy > $temp5
#temp6=$(mktemp -t domath.XXXXXX)
#cut -f 1 -d , $temp5 > $temp6
while read line cp pp percent; do
li+='<li><a target="_blank" href="http://weixin.sogou.com/weixin?query='
left=${stock%($line*} 
li+=${left##*)} 
li+=$line 
li+='&sourceid=inttime_day&tsn=1&fr=sgsearch&type=2">'
li+=$line
li+='</a>'
left=${stock%($line*} 
li+=${left##*)} 
li+=' 采集价：'
li+=$cp
li+='预计价：'
li+=$pp
li+='('
li+=$percent
li+='%)'
li+='</li>'
done < $temp5
span=$(date "+%Y-%m-%d %H:%M")
html=${html/'time'/$span} 
html=${html/'stock'/$li} 

sel=$(mktemp sel.XXXXXX)
sort -n -k 4,2 -t , $temp4 >> $sel
temp7=$(mktemp -t domath.XXXXXX)
head -n 3 $sel > $temp7
li=
while read line cp pp percent; do
li+='<li><a target="_blank" href="http://weixin.sogou.com/weixin?query='
left=${stock%($line*} 
li+=${left##*)} 
li+=$line
li+='&sourceid=inttime_day&tsn=1&fr=sgsearch&type=2">'
li+=$line
li+='</a>'
left=${stock%($line*} 
li+=${left##*)} 
li+=' 采集价：'
li+=$cp
li+='预计价：'
li+=$pp
li+='('
li+=$percent
li+='%)'
li+='</li>'
done < $temp7
html=${html/'sell'/$li} 

temp9=$(mktemp -t domath.XXXXXX)
tail -n 5 'cloudindex.txt' | sort -r > $temp9
li=
while read line; do
li+='<li>'
li+=$line
li+='</li>'
done < $temp9
html=${html/'bull'/$li} 

full=$(mktemp -t domath.XXXXXX)
sort -r -n -k 1,4 -t , $temp4 >> $full
temp6=$(mktemp -t domath.XXXXXX)
head -n 3000 $buy > $temp6
#temp6=$(mktemp -t domath.XXXXXX)
#cut -f 1 -d , $temp5 > $temp6
li=
while read line cp pp percent; do
li+='<li><a target="_blank" href="http://weixin.sogou.com/weixin?query='
left=${stock%($line*} 
li+=${left##*)} 
li+=$line 
li+='&sourceid=inttime_day&tsn=1&fr=sgsearch&type=2">'
li+=$line
li+='</a>'
left=${stock%($line*} 
li+=${left##*)} 
li+=' 采集价：'
li+=$cp
li+='预计价：'
li+=$pp
li+='('
li+=$percent
li+='%)'
li+='</li>'
done < $temp6
span=$(date "+%Y-%m-%d %H:%M")
html=${html/'time'/$span} 
html=${html/'list'/$li} 

now=$(date +%Y-%m-%d);
file="recommend-ann"+$now+".html"
echo $html>$file

IFS=$oldIFS