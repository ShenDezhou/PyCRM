# -*- coding: utf-8 -*-  
import sys
DEBUG = False 

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
            "app_id": "wwwsto.com",
            "mysql_host": '127.0.0.1',
            "mysql_host_slaves": ['127.0.0.1'], 
            "mysql_port": 3306,
            "mysql_user": 'root',
            "mysql_password": "sogou",
            "mysql_database": "fudan_it",
            "mysql_max_conn": 60,
            "mysql_charset": "utf8",
        }
    ]
