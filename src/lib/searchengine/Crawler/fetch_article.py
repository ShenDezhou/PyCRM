# -*- encoding=utf-8 -*-

import urllib
import urllib2
import urlparse
import time
import os
import socket
import logging
from bs4 import BeautifulSoup
import ProxyLoader

# 日志设置
logger = logging.getLogger('Crawler')


def crawl(url, db, round_robin):
    # 请求包配置
    ua = ProxyLoader.get_user_agent()
    req_header = {
        'User-Agent': ua,
        'Accept-Encoding': 'utf-8'
    }

    p = True
    trial = 0
    while p:
        # 勾取代理
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

        # 发送访问请求, 共尝试{trial}次
        abandoned = False
        for i in range(3):
            start_time = time.time()
            req = urllib2.Request(url, None, req_header)
            try:
                response = urllib2.urlopen(req, timeout=5)
            except socket.timeout:
                logger.error('Proxy timeout: ' + p['host'] + ':' + p['port'])
                # 上报数据库此代理已作废
                ProxyLoader.abandon(p)
                abandoned = True
                break
            except urllib2.HTTPError, e:
                logger.warn('HTTPError [{}], retrying...'.format(str(e.code)))
                time.sleep(3)
                continue
            except urllib2.URLError, e:
                logger.warn('URLError [{}], retrying...'.format(str(e.message)))
                print e
                time.sleep(3)
                continue
            else:
                break
        else:
            trial += 1
            if trial >= 3:
                logger.error('Failed: ' + url)
                return
            else:
                ProxyLoader.report(p, 0, 0, url, 'PAGE', False)
                continue

        if abandoned:
            continue

        # 爬取页面内容
        end_time = time.time()
        html = response.read()
        soup = BeautifulSoup(html, 'lxml', from_encoding="utf-8")

        # 抓取文章基本信息
        article_title = soup.find(name="h2", attrs={'id': 'activity-name'})  # 文章标题
        if article_title is None:
            article_title = soup.find(name="h1", attrs={'id': 'activity-name'})
            if article_title is None:
                print html
                logger.error('No TITLE found on: ' + url)
                return
        article_title = article_title.get_text().strip()

        article_date = soup.find(name="em", attrs={'id': 'post-date'})  # 文章发布日期
        if article_date is None:
            article_date = soup.find(name="span", attrs={'id': 'post-date'})
            if article_date is None:
                logger.error('No DATE found on: ' + url)
                return
        article_date = article_date.get_text().strip()

        article_title = str(article_title)
        article_date = str(article_date)
        article_id = urlparse.urlparse(url)[2][3:]          # 文章存储编号

        # 建立文章存储文件夹
        article_path = "storage/article_" + article_id
        if not os.path.exists(article_path):
            os.mkdir(article_path)

        # 抓取文章内容
        content = soup.find(name="div", attrs={'id': 'img-content'})
        if content is None:
            content = soup.find(name="div", attrs={'class': 'wrp_page'})
            if content is None:
                content = soup.find(name="div", attrs={'id': 'essay-body'})
                if content is None:
                    logger.error('No article template found on: ' + url)
                    return
        article_text = content.get_text()                   # 文章纯文本内容
        article_text = article_text.replace('\n', '').replace('\t\t', '').replace('   ', '')
        article_text = str(article_text)
        article_html = unicode(content).encode('utf-8')   # 文章html代码

        # 下载文章中的图片
        article_soup = BeautifulSoup(article_html, 'lxml', from_encoding="utf-8")
        article_imgs = article_soup.findAll(name="img")
        img_id = 0
        for img in article_imgs:
            if img['src'][:4] != 'http':
                continue
            img_id += 1
            urllib.urlretrieve(img['src'], article_path + "/" + str(img_id) + ".jpg")
            # 替换html代码中的图片链接至本地
            img.attrs['src'] = str(img_id) + ".jpg"
        article_html = unicode(article_soup)

        # 将文章写入文件
        with open(article_path + '/content.html', 'w') as f:
            f.write(article_html.encode('utf-8'))

        # 将文章信息写入数据库
        # 45为v_article的第一个clusterId, 12为cluster集, 此方法保证数据在12个集群中分布均匀
        cluster_id = 45 + round_robin
        rec = {
            'id': article_id,
            'title': article_title,
            'date': article_date,
            'save_path': article_path,
            'text': article_text
        }
        rec_pos = db.record_create(cluster_id, rec)
        logger.info('Written into database, rid [{}]'.format(rec_pos._rid))

        # 上报代理信息
        ProxyLoader.report(p, start_time, end_time, url, 'PAGE', True)
        return
