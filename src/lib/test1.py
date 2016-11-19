#/usr/bin/python
#coding=utf-8

import urllib2
from urllib import urlencode
import math
import random
import time

url = "http://wenshu.court.gov.cn/List/ListContent"
#data = "Param=&Index=2&Page=20&Order=%E6%B3%95%E9%99%A2%E5%B1%82%E7%BA%A7&Direction=asc"
inumber = 20
for i in xrange(1, 101):
    dic = {
        "Param":"法院层级:最高法院",
        "Index":i,
        "Page":20,
        "Order":"法院层级",
        "Direction":"asc"
        }
    #data = "Param=%E6%B3%95%E9%99%A2%E5%B1%82%E7%BA%A7%3A%E6%9C%80%E9%AB%98%E6%B3%95%E9%99%A2&Index=%d&Page=%d&Order=%E6%B3%95%E9%99%A2%E5%B1%82%E7%BA%A7&Direction=asc"%(i, 20) #zui gao fa yuan
    data = urlencode(dic)
    request = urllib2.Request(url, data)
    cookies = urllib2.HTTPCookieProcessor()
    request.add_header("Content-Type", "application/x-www-form-urlencoded")
    request.add_header("Encoding", "utf-8")
    request.add_header("Connection", "keep-alive")
    request.add_header("Accept", "*/*")
    request.add_header("Content-Type", "application/x-www-form-urlencoded; charset=UTF-8")
    request.add_header("User-Agent", "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.22 Safari/537.36 SE 2.X MetaSr 1.0")
    request.add_header("X-Requested-With", "XMLHttpRequest")
    request.add_header("Referer", "http://wenshu.court.gov.cn/list/list/?sorttype=1")
    request.add_header("Origin", "http://wenshu.court.gov.cn")
    request.add_header("Host", "wenshu.court.gov.cn")
    print request.get_full_url(), i
    response = urllib2.urlopen(request)

    fout = open(r"F:\caipanwenshu20151106.json", 'a')
    fout.write(response.read()+"\n")
    fout.close()
    time.sleep(random.randrange(1,33))
