#!/bin/bash
# ./auto_deplay_local.sh /project_web_root_pat
#locate_web_root="/home/long/Workspaces/svn/python/asien/web"
locate_web_root=$1
master_server=139.220.240.188
master_server_usr=root
master_server_pwd=2A9#ERwzby


# cd $locate_web_root

# echo "Building the package"

# python build.py 

# echo "Build finished"

# echo "Uploading package to servers"

# cd build
# scp    static/cav/js/mgr_org_form_list.js $master_server_usr@$master_server:/var/marsapp/web/static/cav/js
# scp   views/constants/common_pages.json $master_server_usr@$master_server:/var/marsapp/web/views/constants
scp     $master_server_usr@$master_server:/data/billapp/Crawler/storage.tar        /home/tsingdata/ajkipper/ArticleOfData/Crawler/restorage.tar &