#!/bin/bash
# ./auto_deplay_local.sh /project_web_root_pat
#locate_web_root="/home/long/Workspaces/svn/python/asien/web"
locate_web_root=$1
master_server=app.tsingdata.com
master_server_usr=root
master_server_pwd=cdk@9MIU@#

# cd $locate_web_root

# echo "Building the package"

# python build.py 

# echo "Build finished"

# echo "Uploading package to servers"

# cd build
# scp    static/cav/console/assets/plugins/materialize/css/materialize.css $master_server_usr@$master_server:/var/marsapp/web/static/cav/console/assets/plugins/materialize/css
# scp    static/cav/js/mgr_org_form_list.js $master_server_usr@$master_server:/var/marsapp/web/static/cav/js
# scp    static/cav/js/mgr_member_org_list.js $master_server_usr@$master_server:/var/marsapp/web/static/cav/js
# scp    static/cav/js/mgr_member_person_list.js $master_server_usr@$master_server:/var/marsapp/web/static/cav/js
# scp   static/cav/js/mgr_org_form_normal.js $master_server_usr@$master_server:/var/marsapp/web/static/cav/js
scp	     views/constants/pages.json $master_server_usr@$master_server:/var/marsapp/web/views/constants
# scp	  views/_base.py $master_server_usr@$master_server:/var/marsapp/web/views
# scp   views/corp_page.py $master_server_usr@$master_server:/var/marsapp/web/views
# scp   views/auth.py $master_server_usr@$master_server:/var/marsapp/web/views
# scp    views/lte_util.py $master_server_usr@$master_server:/var/marsapp/web/views
# scp   util/send_phone_email.py $master_server_usr@$master_server:/var/marsapp/web/util
# scp      tpl/simple_appform_vote.html    $master_server_usr@$master_server:/var/marsapp/web/tpl
# scp     tpl/simple_appform_org_normal.html $master_server_usr@$master_server:/var/marsapp/web/tpl
# scp      tpl/simple_appform_person_normal.html  $master_server_usr@$master_server:/var/marsapp/web/tpl
# scp      tpl/header_nav_action.html $master_server_usr@$master_server:/var/marsapp/web/tpl
# scp      tpl/footer_nav_action.html $master_server_usr@$master_server:/var/marsapp/web/tpl
# scp index.py $master_server_usr@$master_server:/var/marsapp/web/
#scp web/project_src.tar.gz $master_server_usr@$master_server:/var/marsfile-sheets/ 
# sshpass -p $master_server_pwd scp web/project_pyc.tar.gz root@$master_server:/var/marsfile-sheets/bin/
echo "Upload package to Master server(NFS) successful"

sshpass -p $master_server_pwd ssh -t $master_server_usr@$master_server 'sudo service supervisord restart' 
echo "Deploy App server successful"


echo "Uploaded and Deployed successful"

echo "All done  ^_^"