#!/usr/bin/python
from app import Monitor

from app import Redis

if __name__ == '__main__':

    monitor = Monitor()
    Redis.delete("refresh")
    monitor.start()
    monitor.join()
