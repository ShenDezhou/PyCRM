#!/usr/bin/python
import threading, time
from command import refresh_machine_resource, refresh_pool_list, refresh_volume_status, \
                     refresh_disk_io, refresh_network_io, volume_create, test1
from command import CONFIG_QUERY_PERIOD
import logging
from redis_util import *


class Monitor(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        count = 0
        while True:
            # try:
            #     while True:
            #         message = Redis.lpop("test1")
            #         if message:
            #             dict_message = eval(message)
            #             print dict_message
            #         else:
            #             break
                # result = test1(test_argu)
                refresh_pool_list()
                determine = Redis.get("Refresh")
                if not determine:
                    refresh_machine_resource()
                    refresh_volume_status()
                else:
                    print determine
                # query_volume_perf()
                # print "helllo3"
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

if __name__ == '__main__':
    Monitor().run()