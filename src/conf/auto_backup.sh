#!/bin/bash

# vi /ect/crontab
# 3 * * * * root /home/meng/hello.sh


# mv /root/backup/marsabank-bk.tar.4 /root/backup/marsabank-bk.tar.5
# mv /root/backup/marsabank-bk.tar.3 /root/backup/marsabank-bk.tar.4
# mv /root/backup/marsabank-bk.tar.2 /root/backup/marsabank-bk.tar.3
# mv /root/backup/marsabank-bk.tar.1 /root/backup/marsabank-bk.tar.2
# mv /root/backup/marsabank-bk.tar /root/backup/marsabank-bk.tar.1

curl https://127.0.0.1/rest/mgr/batchjobs -k &&
service supervisord restart &&
echo "Success"

# mysqldump -u zyyp -pzyyp2015 -h rdss7ntf4wd05ux7xo87.mysql.rds.aliyuncs.com -P 3306 zyyp > /var/marsfile-sheets/bin/marsabank-bk.sql &&

# tar czvf /root/backup/marsabank-bk.tar /var/marsfile-sheets




