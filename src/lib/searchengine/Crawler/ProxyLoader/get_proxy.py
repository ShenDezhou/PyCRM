# -*- encoding=utf-8 -*-

import urllib2
import sys
import pyorient
import env
import time
from bs4 import BeautifulSoup

# 编码设置
reload(sys)
sys.setdefaultencoding('utf-8')

# 高匿代理链接
url = 'http://www.mimiip.com/gngao/' + str(1)

# 爬取高匿代理地址
req = urllib2.Request(url)
html = urllib2.urlopen(req).read()

# 连接数据库
db = pyorient.OrientDB(env.DB_HOST, env.DB_PORT)
db.connect(env.DB_USER, env.DB_PASS)
if db.db_exists(env.DB_NAME, pyorient.STORAGE_TYPE_LOCAL):
    db.db_open(env.DB_NAME, env.DB_USER, env.DB_PASS)
else:
    print "No database"
    db.db_close()
    quit()

# 解析地址
soup = BeautifulSoup(html, 'lxml', from_encoding='utf-8')
proxies = soup.findAll(name='tr')
title = True
for p in proxies:
    if title:
        title = False
        continue
    td = p.findAll(name='td')
    host = td[0].string
    port = int(td[1].string)
    protocol = td[4].string

    query = "SELECT 1 FROM v_proxy WHERE host = '{0}' AND port = {1}".format(host, port)
    if db.query(query):
        continue
    else:
        if protocol != 'HTTP':
            continue
        cmd = '''INSERT INTO v_proxy (
                  host, port, protocol, usage_count, failure_count, success_rate, created_at, avg_time
                  ) VALUES ("{0}", {1}, "{2}", 0, 0, 0, {3}, 0)'''.format(
            host, port, protocol, time.time()
        )
        db.command(cmd)
        print "{0}://{1}:{2} added.".format(protocol.lower(), host, port)

