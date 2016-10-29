#!/bin/bash
# service supervisord stop &&
web_app_root="/var/marsapp/web"
rm -rf $web_app_root/* &&
tar -zvxf project_src.tar.gz -C $web_app_root &&
chown -R root:root $web_app_root &&
chmod -R 755 $web_app_root &&
# service supervisord restart
# rm -rf project_src.tar.gz

#supervisord -c /var/marsabank/web/conf/supervisord-master.conf
