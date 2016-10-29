# -*- encoding=utf-8 -*-

import urllib2
import sys
import pyorient
import time
import logging
import socket
from bs4 import BeautifulSoup
from fetch_article import crawl
import ProxyLoader
from ProxyLoader import env

# 编码设置
reload(sys)
sys.setdefaultencoding('utf-8')

# 日志设置
logger = logging.getLogger('Crawler')
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler('crawler.log')
fh.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
logger.addHandler(fh)
logger.addHandler(ch)
logging.basicConfig(filename='crawler.log', level=logging.DEBUG)

# 获取爬取微信参数
if len(sys.argv) < 2:
    logger.error('No wechat account selected.')
    quit()
account = sys.argv[1]

# 网页链接设置, 并进行相关爬虫初始化准备
ua = ProxyLoader.get_user_agent()
host = 'http://chuansong.me'
url = host + '/account/' + account
req_header = {
    'User-Agent': ua,
    'Accept-Encoding': 'utf-8'
}

# 勾取代理
p = True
trial = 0
while p:
    if url is False:    # 结束爬取
        logger.info('Crawling complete.')
        quit()

    p = ProxyLoader.get()
    if p is False:
        logger.error('NO PROXY. Ending...')
        quit()
    crawl_proxy = urllib2.ProxyHandler({
        p['protocol']: p['host'] + ':' + p['port']
    })
    opener = urllib2.build_opener(crawl_proxy)
    urllib2.install_opener(opener)

    logger.info('Using proxy: ' + p['host'] + ':' + p['port'])

    # 打开账号页面, 寻找所有可以爬取的文章
    start_time = time.time()
    req = urllib2.Request(url, None, req_header)
    try:
        response = urllib2.urlopen(req, timeout=5)
    except socket.timeout:
        logger.error('Proxy timeout: ' + p['host'] + ':' + p['port'])
        # 上报数据库此代理已作废
        ProxyLoader.abandon(p)
        continue
    except Exception as e:
        trial += 1
        logger.warn('Request timeout. Trial ' + str(trial))
        print e
        if trial >= 3:
            logger.error('All trials failure, abandon proxy')
            trial = 0
            ProxyLoader.abandon(p)
        time.sleep(3)
        continue
    end_time = time.time()

    # 计数器清零, 并上报列表页爬取记录
    trial = 0
    ProxyLoader.report(p, start_time, end_time, url, 'LIST', True)

    # 解析列表页面
    try:
        list_html = response.read()
    except socket.timeout:
        ProxyLoader.report(p, start_time, end_time, url, 'LIST', False)
        continue

    list_soup = BeautifulSoup(list_html, 'lxml', from_encoding="utf-8")
    hrefs = list_soup.findAll(name='a', attrs={'class': 'question_link'})
    if len(hrefs) == 0:  # 表示已进入反爬虫页面
        logger.error('Proxy invalid, abandoning: ' + p['host'] + ':' + p['port'])
        ProxyLoader.abandon(p)
        continue

    # 获取下一页链接
    next_page = list_soup.findAll(name='a', attrs={'style': 'float: right'})
    if len(next_page) != 0:  # 确认是否为最后一页
        url = 'http://chuansong.me' + next_page[0]['href']
    else:
        url = False

    # 连接数据库
    db = pyorient.OrientDB(env.DB_HOST, env.DB_PORT)
    db.connect(env.DB_USER, env.DB_PASS)
    if db.db_exists(env.DB_NAME, pyorient.STORAGE_TYPE_LOCAL):
        db.db_open(env.DB_NAME, env.DB_USER, env.DB_PASS)
    else:
        logger.error('Database [{}] does NOT exist.'.format(env.DB_NAME))
        db.db_close()
        quit()

    # 对每一页链接进行爬取
    for a in hrefs:
        try:
            articleId = a['href'][3:]
            result = db.query("SELECT FROM INDEX:v_article.id WHERE key = '{}'".format(articleId))
            if result:
                logger.info('Article already crawled, next')
                continue
                # logger.info('Found crawled article, exiting...')
                # client.db_close()
                # logger.info('Crawling complete!')
                # quit()
            else:
                crawl(url=host + a['href'], db=db, round_robin=int(time.time()) % 12)
        except Exception as e:
            logger.error('An error occurred: ' + e.message + '. URL: ' + host + a['href'])

else:
    logger.error('No available proxies. Ending...')
    quit()

logger.error('THIS SHOULD NOT HAPPEN')
