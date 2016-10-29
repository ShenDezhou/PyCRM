# coding=utf-8

import pyorient
import sys
import os
import os.path

reload(sys)
sys.setdefaultencoding('utf8')

client = pyorient.OrientDB('localhost', 2424)
session_id = client.connect('root', 'tsing1234')
db_name = 'weibo'
db_username = 'root'
db_password = 'tsing1234'

if client.db_exists(db_name, pyorient.STORAGE_TYPE_LOCAL):
    client.db_open(db_name, db_username, db_password)
    print "数据库 [" + db_name + "] 已打开"
else:
    print "数据库 [" + db_name + "] 不存在, 正在退出..."
    sys.exit()

for root, di, lst in os.walk('social/follow'):
    for actorId in lst:
        actor_exist = client.query("SELECT @rid FROM Actor WHERE actorId='{0}'".format(actorId[:-4]))
        if actor_exist:
            actor_rid = actor_exist[0].rid.get()
            print "正在建立 [" + actor_rid +"] 的关系网"
            with open('social/follow/' + actorId, 'r') as f:
                f.readline()    # throw first row title
                line = f.readline()
                while line:
                    following = client.query("SELECT @rid FROM Actor WHERE actorId='{0}'".format(line.split("\t")[0].strip()))
                    if following:
                        follow_rid = following[0].rid.get()
                        print "找到 [" + follow_rid + "]"
                        client.command("CREATE EDGE Follow FROM #{0} TO #{1}".format(actor_rid, follow_rid))

                    line = f.readline()
        else:
            print "----- 未找到演员 -----"

client.db_close()
print "数据库 [" + db_name + "] 已关闭"
