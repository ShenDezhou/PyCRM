#!/bin/bash
# ./auto_deplay_local.sh /project_web_root_pat
#locate_web_root="/home/long/Workspaces/svn/python/asien/web"
locate_web_root=$1
master_server=wwwsto.com
master_server_usr=root
master_server_pwd=

cd $locate_web_root

echo "Building the package"

python build.py 

echo "Build finished"

echo "Uploading package to servers"

cd build



# scp web/project_src.tar.gz $master_server_usr@$master_server:/var/marsfile-sheets/bin/ 
# # sshpass -p $master_server_pwd scp web/project_pyc.tar.gz root@$master_server:/var/marsfile-sheets/bin/
# echo "Upload package to Master server(NFS) successful"

# sshpass -p $master_server_pwd ssh -t $master_server_usr@$master_server 'cd /var/marsfile-sheets/bin/ && sudo sh /var/marsfile-sheets/bin/conf/auto_deploy.sh && sudo service supervisord restart' 
# echo "Deploy App server successful"


echo "Uploaded and Deployed successful"

echo "All done  ^_^"
