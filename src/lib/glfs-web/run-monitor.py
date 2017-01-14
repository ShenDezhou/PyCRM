#!/usr/bin/python
from app import Monitor

from app import Redis
import time

if __name__ == '__main__':
    time.sleep(1)
    monitor = Monitor()
    monitor.start()
    monitor.join()

