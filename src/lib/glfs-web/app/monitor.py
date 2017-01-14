import threading, time
from command import refresh_machine_resource, refresh_pool_list, refresh_volume_status, \
                     refresh_disk_io, refresh_network_io
from command import CONFIG_QUERY_PERIOD, volume_create
import logging
from redis_util import *
# from celery import Celery
# celery = Celery('tasks', broker='redis://localhost:6379/0')
#_executor
import subprocess
import os
import re
import sys
from executor import *

class Monitor(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        localExecutor = LocalExecutor()

    def run(self):
        count = 0
        while True:
            # try:
                while True:
                    cmd = Redis.lpop(VIEW_MONITOR)
                    print 'lpop',cmd
                    if not cmd:
                        break
                    else:
                        if type(cmd) is types.ListType:
                            result = localExecutor.execute(cmd[0:-2],cmd[-1])
                        else:#string
                            result = localExecutor.execute_confirm(cmd)
                        print 'lpush',result
                        Redis.lpush(MONITOR_VIEW,result)

                res = refresh_pool_list()
                determine = Redis.get("Refresh")
                if not determine:
                    print "helloh"
                    refresh_machine_resource()
                    refresh_volume_status()
                else:
                    print determine

                # query_volume_perf()
                refresh_disk_io()
                refresh_network_io()
                time.sleep(5)
                count += 1
                if count == 12:
                    # refresh_volume_data()
                    count = 0
            # except Exception, e:
            #     logging.warning(e)
            #     break


# if __name__ == '__main__':
#     Monitor().run()
