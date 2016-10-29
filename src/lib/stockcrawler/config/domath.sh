#!/bin/bash
#100000,200,12341234,4300303
#*************************
#100000,200*200/1,2*2
temp0=$(mktemp -t domath.XXXXXX)
temp1=$(mktemp -t domath.XXXXXX)
temp2=$(mktemp -t domath.XXXXXX)
temp3=$(mktemp -t domath.XXXXXX)
temp4=$(mktemp -t domath.XXXXXX)
cut -f 1 -d , $1 >> $temp0
cut -f 2 -d , $1 | while read line; do
echo $(($line)) >> $temp1;
done
now=$(date +%Y-%m-%d);
cut -f 3 -d , $1 | while read lastts; do
echo $lastts >> $temp2;
done

sum=0  
data=`cut -f 2 -d , $1`  
for i in $data  
do 
    sum=$(($sum+$i))  
done

ratio=86400*3*2/$sum

cut -f 2,3 -d , $1 | while read cmath; do
echo $(($((${cmath%,*} * $ratio))+ ${cmath#*,} )) >> $temp3;
done
paste -d , $temp0 $temp1 $temp2 $temp3 >> $temp4


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
sort -r -n -k 2,3 -t , $temp4 >> $buy
read html< "recommend-tpl.html"
temp5=$(mktemp -t domath.XXXXXX)
head -n 3 $buy > $temp5
temp6=$(mktemp -t domath.XXXXXX)
cut -f 1 -d , $temp5 > $temp6
while read line; do
li+='<li><a target="_blank" href="http://weixin.sogou.com/weixin?query='
left=${stock%($line*} 
li+=${left##*)} 
li+=$line 
li+='&sourceid=inttime_day&tsn=1&fr=sgsearch&type=2">'
li+=$line
li+='</a>'
left=${stock%($line*} 
li+=${left##*)} 
li+='</li>'
done < $temp6
span=$(date "+%Y-%m-%d %H:%M")
html=${html/'time'/$span} 
html=${html/'stock'/$li} 
#echo $html
#echo $html>"recommend.html"

temp7=$(mktemp -t domath.XXXXXX)
sel=$(mktemp sel.XXXXXX)
sort -r -n -k 4,4 -t , $temp4 >> $sel
head -n 3 $sel > $temp7
temp8=$(mktemp -t domath.XXXXXX)
cut -f 1 -d , $temp7 > $temp8
li=
while read line; do
li+='<li><a target="_blank" href="http://weixin.sogou.com/weixin?query='
left=${stock%($line*} 
li+=${left##*)} 
li+=$line
li+='&sourceid=inttime_day&tsn=1&fr=sgsearch&type=2">'
li+=$line
li+='</a>'
left=${stock%($line*} 
li+=${left##*)} 
li+='</li>'
done < $temp8
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
#echo $html
file="recommend"+$now+".html"
echo $html>$file
