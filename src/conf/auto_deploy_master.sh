#!/bin/bash
# service supervisord stop &&
sleep 2s
#bin_dir="/var/marsfile-sheets/bin"
web_app_root="/var/marsabank/web"
rm -rf $web_app_root/* &&
tar -zvxf project_pyc.tar.gz -C $web_app_root &&
chown -R root:root $web_app_root &&
chmod -R 755 $web_app_root &&
sleep 1s &&
service supervisord restart
# rm -rf project_src.tar.gz

# sudo supervisord -c /var/marsfile-sheets/bin/conf/supervisord-master.conf

