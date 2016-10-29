
# coding: utf-8

# In[1]:

get_ipython().system(u'pip install BeautifulSoup4')


# In[11]:






# In[12]:


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
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s - %(asctime)s %(message)s', datefmt='[%b %d %H:%M:%S]')
span=86
use_proxy=False
proxyid = 0
path=sys.path[0]
def getHtml(code,use_proxy=False):
    #code = 600663
    qstr = urllib.quote(get_fulname("%06d"%code).encode("UTF-8"))
    d = datetime.utcnow()
    ts = calendar.timegm(d.utctimetuple())
    #print qstr
    # data = urllib.urlencode(values)
    if use_proxy :
        url = u"http://weixin.sogou.com/weixin?sourceid=inttime_day&tsn=1&type=2&query=%s&fr=sgsearch&ie=utf8&_ast=%d&_asf=null&w=%08d&cid=null" % (qstr,ts,random.randint(0,100000000))
        # proxyip = '121.14.138.56:81'
        proxyip = proxypool[proxyid]
        # proxypool = ['111.161.65.79:80','163.177.79.5:80','39.79.139.31:80','182.254.129.90:8080'
        logging.info("using proxy:%s"%proxyip)
        headers = { 'User-Agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36',
                'Referer':'http://weixin.sogou.com/',
                'Cookie':'ABTEST=4|1438271704|v1; IPLOC=CN88; SUID=AB02E6676A20900A0000000055BA48D8; SUV=0086783667E602AB55BA48DAF6966090; SUID=AB02E6677310920A0000000055BA48DA; weixinIndexVisited=1; sct=1; SNUID=%s' % '5B1078CF1B1E078F734094041C63B1BC',
                'Accept-Encoding':'gzip, deflate, sdch',
                'Accept-Language':'zh-cn,zh;q=0.8,en-us;q=0.5,en;q=0.3',
                'Cache-Control':'max-age=0',
                'Connection':'keep-alive',
                'Host':'weixin.sogou.com'
                }
        if proxyid % 2 ==0:
            headers['Cookie']= 'ABTEST=5|1437318971|v1; IPLOC=CN1100; SUID=470B64D32708930A0000000055ABBF3B; SUV=1438272036284458; SUID=AB02E6677310920A0000000055BA4A22; weixinIndexVisited=1; sct=1; SNUID=%s; wapsogou_qq_nickname=' % 'B51CF9791E1B031C10DEB60C1FF02365'
        req = urllib2.Request(url,headers = headers)
        proxy = urllib2.ProxyHandler({'http': proxyip})
        opener = urllib2.build_opener(proxy)
        #urllib2.install_opener(opener)
        response = opener.open(req,timeout=10)
    else:    
        url = u"http://weixin.sogou.com/weixin?sourceid=inttime_day&tsn=1&type=2&query=%s&fr=sgsearch&ie=utf8&_ast=%d&_asf=null&w=%08d&cid=null" % (qstr,ts,random.randint(0,100000000))
        logging.info("using NO proxy.")
        headers = { 'User-Agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:37.0) Gecko/20100101 Firefox/37.0',
                'Referer':'http://weixin.sogou.com/',
                'Cookie':'SUV=1209062227293584; CXID=AB4DFBC95A62C282FC5697930A8A82E0; IPLOC=CN1100; ssuid=3271513620; SUID=E4FF276A5709950A54BE423300016CE9; weixinIndexVisited=1; sct=24; ad=$UlPNyllll2q5H3flllllVqlRyllllll1LyRDyllllZlllll4llll5@@@@@@@@@@; SNUID=%s; ABTEST=7|1431385763|v1; wapsogou_qq_nickname=' % '8E8B9602DEDBC08C80B679A1DE652CCB',
                'Accept-Encoding':'gzip, deflate',
                'Accept-Language':'zh-cn,zh;q=0.8,en-us;q=0.5,en;q=0.3',
                'Cache-Control':'max-age=0',
                'Connection':'keep-alive',
                'Host':'weixin.sogou.com'
                }
        req = urllib2.Request(url,headers = headers)
        response = urllib2.urlopen(req)
    respInfo = response.info()
    if "Content-Encoding" in respInfo and respInfo['Content-Encoding'] == "gzip":
        #logging.info("using Gzip compressed.")
        compresseddata = response.read()
        #print compresseddata
        compressedstream = StringIO.StringIO(compresseddata)
        gzipper = gzip.GzipFile(fileobj=compressedstream)
        html = gzipper.read()
    else:
        #logging.info("using NO compression.")
        html = response.read()
    #print html
    if anti_spider(html)>0:
        return False;
    # return 
    soup = BeautifulSoup(html)
    c = "%06d"%code

    if soup.find('div', { "class" : "s-p" }):
        t = soup.findAll('div', { "class" : "s-p" })
        n = str(len(t))
        if soup.find("resnum"):
            n = soup.find("resnum").contents[0]
        l= []
        for e in t:
            l.append(int(e['t']))
        #print l
        t = str(sum(l)/len(l))
    else:
        n = '0'
        t = '0'

    pos_reg = ur'大|增|强劲|反弹|上涨|合理|买入|维持|反转|扭亏|一定|持续|改善|受益|满仓'
    posre = re.compile(pos_reg)
    poslist = re.findall(posre,soup.get_text())
    pn = len(poslist)

    neg_reg = ur'小|减|疲软|放缓|下跌|衰退|卖出|下调|亏损|下降|可能|中止|恶化|影响|空仓'
    negre = re.compile(neg_reg)
    neglist = re.findall(negre,soup.get_text())
    nn = len(neglist)
    if (pn - nn) != 0:
        n = str(int(n) * (pn - nn))

    save_line("%s,%s,%s,%s,%s"%(c,n.replace(',',''),pn,nn,t))
    logging.info("saved data: %s,%s,%s,%s,%s"%(c,n.replace(',',''),pn,nn,t))
    return True
def anti_spider(html):
    reg = r'src="seccode.php\?tc=\d+"'
    imgre = re.compile(reg)
    imglist = re.findall(imgre,html)
    # print imglist
    return len(imglist)

def save_line(line):
    ctime = time.strftime('%Y-%m-%d', time.gmtime(time.time()+8*3600))
    with open('save%s.txt' % ctime, 'ab') as fp:
        fp.write('%s\n' % (line.strip()))
        
def save_status(line):
    # ctime = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()+8*3600))
    with open('status.txt', 'w+') as fp:
        fp.seek(0)
        fp.write('%s\n' % (line.strip()))
        
def read_status():
    # ctime = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()+8*3600))
    
    with open('status.txt', 'r+') as fp:
        line= fp.readline()
        if len(line)==0:
            return 1;
        return int(line)    
    return 1;

proxypool=[]
def read_ip():
    # ctime = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()+8*3600))
    with open('ip.txt', 'r+') as fp:
        for line in fp.readlines():
            words = line.split('\t')
            proxypool.append('%s:%s'%(words[0].strip(),words[1].strip()))
    random.shuffle(proxypool)
    
stockinfo =u""

def check_valid(stock):
    if stockinfo.find(stock) > -1 :
        return True
    return False
 
def get_fulname(stock):
    reg = r'(%s)'%stock
    i = stockinfo.index(reg)
    j = stockinfo[:i].rindex(r')')
    return stockinfo[j+1:i]+stock
       
#html = "http://weixin.sogou.com/weixin?query=600111&type=2"
mailto_list=['bangtech@sina.com','gaohaiyuancc@163.com','viewtech@yeah.net','michael.lidaming@gmail.com','ranwangx@gmail.com','liwenshujlu@gmail.com','qililiqq@gmail.com','liu.jfchina@gmail.com','52479395@qq.com','652601418@qq.com','WinnDiXie@foxmail.com','asmilencer@126.com','hongyao21@163.com','52808671@qq.com','75256111@qq.com','gdw99@163.com','aggie_cc@163.com','245522831@qq.com','jennadudu@126.com','extend2010@126.com','2086704695@qq.com','liujuchong@163.com','sadechai@outlook.com','74889408@163.com','16791701@qq.com','zhangyj0330@163.com','yezulong@163.com','153872268@qq.com','953755977@qq.com','dengchidengchi@126.com','yekaichen@sina.com'] 
mailto_list_dbg=['bangtech@sina.com']
mail_host="smtp.sina.com"  #设置服务器
mail_user="stockpredict"    #用户名
mail_pass="stockpredict"   #口令 
mail_postfix="sina.com"  #发件箱的后缀
trycount=0
spidercount=0  

def read_email():
    del mailto_list[:]
    with open('email.txt', 'r+') as fp:
        for line in fp.readlines():
            words = line.strip().split(',')
            for mail in words:
                mailto_list.append(mail.strip('\''))




def send_mail(account_index,to_list,sub,content):  
    me="stockpredict_via_wechat_bigdata"+"<"+mail_user+"@"+mail_postfix+">"  
    msg = MIMEText(content,_subtype='html',_charset='UTF-8')   
    msg['Subject'] = sub  
    msg['From'] = me  
    msg['To'] = to_list[0] 
    msg['Bcc'] = ";".join(to_list[1:])   
    try:  
        server = smtplib.SMTP()  
        server.connect(mail_host) 
        if account_index>0:
            server.login('%s%d'%(mail_user,account_index),mail_pass) 
        else:
            server.login(mail_user,mail_pass)  
        server.sendmail(me, to_list, msg.as_string())  
        server.close()  
        return True  
    except Exception, e:  
        print str(e)  
        return False  


def domath_sendrep(count):
    print('info get: %d!'%count)    
    ctime = time.strftime('%Y-%m-%d', time.gmtime(time.time()+8*3600))
    timelst = []
    for i in range(0,3):
        timelst.append(time.strftime('%Y-%m-%d', time.gmtime(time.time()+8*3600-i*24*3600)))
    cmd = 'cat'
    for timestr in timelst:
        cmd += ' save%s.txt'%timestr
    cmd += '>'
    tmp = 'save.%06d' % random.randint(0,1000000)
    cmd += tmp
    print(cmd)
    os.system(cmd)
    print('domath...')
    os.system("bash ./domath.sh %s" % tmp)
    trycount=0
    with open('recommend+%s+.html'%ctime, 'r+') as fp:
        recommend= fp.readline().decode("UTF-8" )
        ctime = time.strftime('%Y-%m-%d %H:%M', time.gmtime(time.time()+8*3600))
        read_email() 
        step=30
        try: 
            for i in range(0,len(mailto_list)/step + 1):
                print(recommend.encode("UTF-8"))
                #if count> 20 and send_mail(i,mailto_list[i*step:i*step+29],u"股市有风险 投资需谨慎:云上犇牛实时推荐%s"%ctime,recommend.encode("UTF-8")):  
                #    logging.info('Destination:%s'%";".join(mailto_list[i*step:i*step+29]) )
                logging.info('mail sent!')
        except Exception, e:  
            logging.exception('sendmail error: %r', e)

logging.info(path)
read_ip()
logging.info(proxypool)
count = 0
with open('astock.txt', 'r+') as fp:
    astockinfo= fp.readline().decode("UTF-8" )
with open('sstock.txt', 'r+') as fp:
    sstockinfo= fp.readline().decode("UTF-8" )
with open('rstock.txt', 'r+') as fp:
    rstockinfo= fp.readline().decode("UTF-8" )
stockinfo = astockinfo + sstockinfo + rstockinfo


try:
    x = read_status()
    if check_valid("%06d"%x):
        use_proxy = False
        if False==getHtml(x,use_proxy):
            spidercount+=1
            x-=1
            logging.info('%s met antispider, spider counter:%d!'%(x,spidercount))
            logging.info("%r removed from list",proxypool[proxyid])
            proxypool.remove(proxypool[proxyid])
            if spidercount > 99:
                logging.info('%06d met antispider, game over!'%x)
                #break;
        #time.sleep(span)
    else:
        logging.info('%06d is not valid stock' %x)
except Exception as e:
    logging.exception('proxy error: %r', e)
    if 'timed out' in str(e) or 'Connection refused' in str(e) or 'Connection reset by peer' in str(e) or 'Forbidden' in str(e) or 'Access Denied' in str(e) or 'No route to host' in str(e) or 'Bad Gateway' in str(e) or 'Not Found' in str(e) or 'Service Unavailable' in str(e) or 'BadStatusLine' in '%r' % e:
        x-=1
        logging.info("%r removed from list",proxypool[proxyid])
        proxypool.remove(proxypool[proxyid])
finally:
    if check_valid("%06d"%x):
        proxyid+=1
        proxyid %=30
        if proxyid >= len(proxypool)-1:
            proxyid = 0
        if len(proxypool) < 5:
            read_ip()
            spidercount=0
        count += 1
        time.sleep(0.05)
    else:
        time.sleep(0.05)
    x+=1
    if x>3000 and x<159900:
        x=159900

    if x>159944 and x<300000:
        x=300000

    if x>300500 and x<510010:
        x=510010

    if x>518880 and x<600000:
        x=600000

    save_status("%06d"%x)
    if x>604000:
        x=0
        save_status("%06d"%x)
        #domath_sendrep(count)
        #count=0
        logging.info('INFO GET, JOB FINISHED')
        # continue;
    if count > 1000:
        domath_sendrep(count)
        count=0
        logging.info('INFO GET, JOB FINISHED')
        # continue;

print('new message got!')




# In[12]:

get_ipython().system(u'cat save2015-08-16.txt')


# In[37]:

import math
import random
import string
from numpy  import *

random.seed(0)

# calculate a random number where:  a <= rand < b
def rand(a, b):
    return (b-a)*random.random() + a

# Make a matrix (we could use NumPy to speed this up)
def makeMatrix(I, J, fill=0.0):
    m = []
    for i in range(I):
        m.append([fill]*J)
    return m

# our sigmoid function, tanh is a little nicer than the standard 1/(1+e^-x)
#使用双正切函数代替logistic函数
def sigmoid(x):
    return math.tanh(x)

# derivative of our sigmoid function, in terms of the output (i.e. y)
# 双正切函数的导数，在求取输出层和隐藏侧的误差项的时候会用到
def dsigmoid(y):
    return 1.0 - y**2

class NN:
    def __init__(self, ni, nh, no):
        # number of input, hidden, and output nodes
        # 输入层，隐藏层，输出层的数量，三层网络
        self.ni = ni # +1 for bias node
        self.nh = nh
        self.no = no

        # activations for nodes
        self.ai = [1.0]*self.ni
        self.ah = [1.0]*self.nh
        self.ao = [1.0]*self.no
        
        # create weights
        #生成权重矩阵，每一个输入层节点和隐藏层节点都连接
        #每一个隐藏层节点和输出层节点链接
        #大小：self.ni*self.nh
        self.wi = makeMatrix(self.ni, self.nh)
        #大小：self.ni*self.nh
        self.wo = makeMatrix(self.nh, self.no)
        # set them to random vaules
        #生成权重，在-0.2-0.2之间
        for i in range(self.ni):
            for j in range(self.nh):
                self.wi[i][j] = rand(-0.2, 0.2)
        for j in range(self.nh):
            for k in range(self.no):
                self.wo[j][k] = rand(-2.0, 2.0)

        # last change in weights for momentum 
        #?
        self.ci = makeMatrix(self.ni, self.nh)
        self.co = makeMatrix(self.nh, self.no)

    def update(self, inputs):
        if len(inputs) != self.ni:
            raise ValueError('wrong number of inputs')

        # input activations
        # 输入的激活函数，就是y=x;
        for i in range(self.ni):
            #self.ai[i] = sigmoid(inputs[i])
            self.ai[i] = inputs[i]

        # hidden activations
        #隐藏层的激活函数,求和然后使用压缩函数
        for j in range(self.nh):
            sum = 0.0
            for i in range(self.ni):
                #sum就是《ml》书中的net
                sum = sum + self.ai[i] * self.wi[i][j]
            self.ah[j] = sigmoid(sum)

        # output activations
        #输出的激活函数
        for k in range(self.no):
            sum = 0.0
            for j in range(self.nh):
                sum = sum + self.ah[j] * self.wo[j][k]
            self.ao[k] = sigmoid(sum)

        return self.ao[:]

    #反向传播算法 targets是样本的正确的输出
    def backPropagate(self, targets, N, M):
        if len(targets) != self.no:
            raise ValueError('wrong number of target values')

        # calculate error terms for output
        #计算输出层的误差项 
        output_deltas = [0.0] * self.no
        for k in range(self.no):
            #计算k-o
            error = targets[k]-self.ao[k]
            #计算书中公式4.14
            output_deltas[k] = dsigmoid(self.ao[k]) * error

        # calculate error terms for hidden
        #计算隐藏层的误差项，使用《ml》书中的公式4.15
        hidden_deltas = [0.0] * self.nh
        for j in range(self.nh):
            error = 0.0
            for k in range(self.no):
                error = error + output_deltas[k]*self.wo[j][k]
            hidden_deltas[j] = dsigmoid(self.ah[j]) * error

        # update output weights
        # 更新输出层的权重参数
        # 这里可以看出，本例使用的是带有“增加冲量项”的BPANN
        # 其中，N为学习速率 M为充量项的参数 self.co为冲量项
        # N: learning rate
        # M: momentum factor
        for j in range(self.nh):
            for k in range(self.no):
                change = output_deltas[k]*self.ah[j]
                self.wo[j][k] = self.wo[j][k] + N*change + M*self.co[j][k]
                self.co[j][k] = change
                #print N*change, M*self.co[j][k]

        # update input weights
        #更新输入项的权重参数
        for i in range(self.ni):
            for j in range(self.nh):
                change = hidden_deltas[j]*self.ai[i]
                self.wi[i][j] = self.wi[i][j] + N*change + M*self.ci[i][j]
                self.ci[i][j] = change

        # calculate error
        #计算E(w)
        error = 0.0
        for k in range(len(targets)):
            error = error + 0.5*(targets[k]-self.ao[k])**2
        return error

    #测试函数，用于测试训练效果
    def test(self, patterns):
        for p in patterns:
            print(p[0], '->', self.update(p[0]))

    def weights(self):
        print('Input weights:')
        for i in range(self.ni):
            print(self.wi[i])
        print()
        print('Output weights:')
        for j in range(self.nh):
            print(self.wo[j])

    def train(self, patterns, iterations=1000, N=0.5, M=0.1):
        # N: learning rate
        # M: momentum factor
        for i in range(iterations):
            error = 0.0
            for p in patterns:
                inputs = p[0]
                targets = p[1]
                self.update(inputs)
                error = error + self.backPropagate(targets, N, M)
            if i % 100 == 0:
                print('error %-.5f' % error)



# In[97]:

data = sc.textFile("rawdata.txt")

def parse(line):
    arr=line.split(',')
    return [[float(arr[1])/1000,float(arr[2])/1000,float(arr[3])/1000],[float(arr[4])/1000]]

parsedData = data.map(parse)
#print parsedData.take(5)
#print (parsedData.count())
n = NN(3, 1, 1)
print 'training...'
n.train(parsedData.take(100))
print 'testing...'
n.test(parsedData.take(100))
print 'test done'





# In[38]:


fresh = sc.textFile("save2015-08-16.txt")
freshData = fresh.map(parse)
news = freshData.take(1)[0][0]
predictedPrice=n.update(news)[0]
print (news,'->',predictedPrice)
print 'prediction complete'



# In[39]:

get_ipython().system(u'cat save2015-08-16.txt')


# In[33]:




# In[43]:

import os  
import math  
import pylab  

y_values = []  
x_values = []  
specific = data.filter(lambda l:'600528' in l)
i=1
for line in specific.collect():
    x_values.append(i)
    y_values.append(line.split(',')[4])
    i+=1

fresh = sc.textFile("save2015-08-16.txt")
freshData = fresh.map(parse)
news = freshData.take(1)[0][0]
predictedPrice=n.update(news)[0]
print (news,'->',predictedPrice)
print 'prediction complete'

x_values.append(i+1)
y_values.append(predictedPrice*1000)

  
pylab.plot(x_values,y_values)  
pylab.show()  


# In[41]:

domath_sendrep(1000)


# In[42]:

print 'Thank You!'


# In[ ]:



