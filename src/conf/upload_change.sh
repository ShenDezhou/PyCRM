#!/bin/bash
# using git log to retrieve changed file and use scp to upload file and restart it.
web_dir=/var/marsapp/web
master_server=wwwsto.com
master_server_usr=root
master_server_pwd=cdk@9MIU@#


#git log --stat -4 > git.log

regex='(.+)\|'

if [[ $# == 1 ]]; then
    git log --stat -$1 > git.log
else
    git log --stat -1 > git.log
fi

echo "regex: $regex"
echo
while read line ;
do
    if [[ $line =~ $regex ]]; then
        echo "$line matches"
        i=1
        filename=${BASH_REMATCH[$i]}
        echo "  capture[$i]: $filename"
        folder="$(dirname $filename)"
        scp $filename $master_server_usr@$master_server:$web_dir/$folder
    fi
done < git.log

echo "Upload package to Master server(NFS) successful"

sshpass -p $master_server_pwd ssh -t $master_server_usr@$master_server 'sudo service supervisord restart' 
echo "Deploy App server successful"


echo "Uploaded and Deployed successful"

echo "All done  ^_^"
