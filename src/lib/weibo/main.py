# encoding: UTF-8

import os
import subprocess
import threading

def popen(f):
    pargs = [r"D:\Python27\Python.exe", f]
    subprocess.Popen(pargs).wait()

threads = []
processor = ['weibo.py','trim.py','reduce.py']
for f in processor:
    t = threading.Thread(target=popen,args=(f,))
    threads.append(t)

for t in threads:
    t.setDaemon(True)
    t.start()

for t in threads:
    t.join()

print 'job done'