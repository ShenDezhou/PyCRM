# coding=utf-8

import pyorient
import sys

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

with open('social/actorId.txt', 'r') as f:
    f.readline()  # throw first row title
    line = f.readline()
    # for i in range(0, 100):
    while line:
        actorInfo = line.split("\t")
        if len(actorInfo) == 3:
            query = r"INSERT INTO Actor SET fans={0}, verifyName='{1}', actorId='{2}'".format(
                actorInfo[0].strip(), actorInfo[1].strip(), actorInfo[2].strip()
            )
        else:
            query = r"INSERT INTO Actor SET fans={0}, verifyName='{1}', actorId='{2}', preferredName='{3}', actorDesc='{4}'".format(
                actorInfo[0].strip(), actorInfo[1].strip(), actorInfo[2].strip(), actorInfo[3].strip(), actorInfo[4].strip()
            )
        # print query
        ret = client.command(query)
        print "写入: " + str(ret)
        line = f.readline()

client.db_close()
print "数据库 [" + db_name + "] 已关闭"
