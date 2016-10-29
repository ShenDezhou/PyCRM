# -*- coding: utf-8 -*-  

import sys

DEBUG = True

if 'tax' in sys.argv[0] or 'tax.queue' in ','.join(sys.argv):
	print 'Using Tax Config Settings'
	from config_tax import settings as settings_web 
else:
	print 'Using Web Config Settings'
	from config_web import settings as settings_web 

import socket

settings = settings_web


if DEBUG:

    settings['production'] = False

    settings['debug'] = True


    settings["apps"] = [
        {
            # 应用唯一号
            "app_id": "172.16.168.136",
            # mysql 主服务器IP
            "mysql_host": '127.0.0.1',
            # mysql 从服务器IP
            "mysql_host_slaves": ['127.0.0.1'], 
            # mysql 端口号
            "mysql_port": 3306,
            # mysql 用户名
            "mysql_user": 'root',
            # mysql 密码
            "mysql_password": "asiencredit",
            # mysql 数据库名
            "mysql_database": "marsapp",
            "mysql_max_conn": 60,
            # mysql 字符编码
            "mysql_charset": "utf8",
        }
    ]