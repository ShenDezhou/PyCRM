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
            # åºç¨å¯ä¸å·
            "app_id": "wwwsto.com",
            # mysql ä¸»æå¡å¨IP
            "mysql_host": '127.0.0.1',
            # mysql ä»æå¡å¨IP
            "mysql_host_slaves": ['127.0.0.1'], 
            # mysql ç«¯å£å·
            "mysql_port": 3306,
            # mysql ç¨æ·å
            "mysql_user": 'root',
            # mysql å¯ç 
            "mysql_password": "Wwwsto@2017",
            # mysql æ°æ®åºå
            "mysql_database": "fudan_it",
            "mysql_max_conn": 60,
            # mysql å­ç¬¦ç¼ç 
            "mysql_charset": "utf8",
        }
    ]
