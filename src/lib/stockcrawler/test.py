#coding=utf-8
import urllib
import urllib2
import re
from bs4 import BeautifulSoup
import StringIO
import gzip
import random
import time
import collections
import logging
import sys,os
import smtplib  
from email.mime.text import MIMEText  
import random
from datetime import datetime
import calendar
#reload(sys)
#sys.setdefaultencoding("utf-8")
path=sys.path[0]
mailto_list=[]
def read_email():
    del mailto_list[:]
    with open(os.path.join(path,'email.txt'), 'r+') as fp:
        for line in fp.readlines():
            words = line.strip().split(',')
            for mail in words:
                mailto_list.append(mail.strip('\''))

if __name__ == '__main__':
    read_email()
    print ';'.join(mailto_list)
