# -*- coding: utf-8 -*-  
# 
from selenium import webdriver
import selenium
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from bs4 import BeautifulSoup
import requests
import logging
import re
import time
from urllib import quote
import random

BASE_URL = 'http://weixin.sogou.com'

UA = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36"

def get_html(url):
    dcap = dict(DesiredCapabilities.PHANTOMJS)
    dcap["phantomjs.page.settings.userAgent"] = (
        UA
    )
    dcap["takesScreenshot"] = (False)
    #t0 = time.time()
    try:
        driver = webdriver.PhantomJS(desired_capabilities=dcap, service_args=['--load-images=no'])
        driver.set_page_load_timeout(240)
        driver.command_executor._commands['executePhantomScript'] = ('POST', '/session/$sessionId/phantom/execute')

        driver.execute('executePhantomScript', {'script': '''
            var page = this; // won't work otherwise
            page.onResourceRequested = function(requestData, request) {
                if ((/http:\/\/.+?\.css/gi).test(requestData['url']) || requestData['Content-Type'] == 'text/css') {
                    console.log('The url of the request is matching. Aborting: ' + requestData['url']);
                    request.abort();
                }
            }
            ''', 'args': []})
    except selenium.common.exceptions.WebDriverException:
        return None
    try:
        driver.get(url)
        html = driver.page_source
    except Exception as e:
        html = None
        logging.error(e)
    finally:
        driver.quit()
    return html

def get_html_direct(url,cookies=None):
    if not cookies:
        cookies = update_cookies()
    headers = {"User-Agent": UA}
    r = requests.get(url, headers=headers, cookies=cookies, timeout=20)
    return r.text

def get_account_info(open_id=None, link=None, cookies=None):
    url = None
    if open_id:
        url = BASE_URL + '/gzh?openid=' + open_id
    if link:
        url = link
    #html = get_html(url)
    html = get_html_direct(url, cookies=cookies)
    #print(html)
    if not html:
        return None
    soup = BeautifulSoup(html, "lxml")
    info_box = soup.select('#weixinname')[0].parent
    account_info = {}
    account_info['account'] = info_box.select('h4 span')[0].text.split('：')[1].strip()
    account_info['name'] = info_box.select('#weixinname')[0].text
    account_info['address'] = url
    account_info['description'] = info_box.select('.sp-txt')[0].text
    img_list = soup.select('.pos-box img')
    account_info['logo'] = soup.select(".img-box img")[0]['src']
    account_info['qr_code'] = img_list[1]['src']
    return account_info


def parse_list(open_id=None, link=None):
    if open_id:
        url = BASE_URL + '/gzh?openid=' + open_id
    elif link:
        url = link
    else:
        return None
    html = get_html(url)
    if not html:
        return None
    soup = BeautifulSoup(html)
    ls = soup.select('#wxbox .txt-box')
    link_list = []
    for item in ls:
        item_dict = {}
        item_dict['title'] = item.a.text
        item_dict['link'] = item.a['href']
        link_list.append(item_dict)
    return link_list


def parse_essay(link):
    s = requests.Session()
    s.headers.update({"User-Agent": UA})
    try:
        r = s.get(link, verify=False)
        html = r.text
        soup = BeautifulSoup(html)
        essay = {}
        p = re.compile(r'\?wx_fmt.+?\"')
        content = str(soup.select("#js_content")[0]).replace('data-src', 'src')
        essay['content'] = re.sub(p, '"', content).strip()
        essay['name'] = soup.select('#post-user')[0].text.strip()
        essay['date'] = soup.select('#post-date')[0].text.strip()
        essay['title'] = soup.select('#activity-name')[0].text.strip()
    except Exception:
        return None

    return essay


def weixin_search(name, cookies=None):
    url = BASE_URL + '/weixin?query=' + name
    #html = get_html(url)
    html = get_html_direct(url, cookies=cookies)
    print(html)
    soup = BeautifulSoup(html)
    ls = soup.select("._item")
    search_list = []
    for item in ls:
        account_info = {}
        account_info['account'] = item.select('h4 span')[0].text.split('：')[1].strip()
        account_info['name'] = item.select('.txt-box h3')[0].text
        account_info['address'] = BASE_URL + item['href']
        account_info['open_id'] = item['href'].split('openid=')[1]
        account_info['description'] = item.select('.sp-txt')[0].text
        account_info['logo'] = item.select('.img-box img')[0]['src']
        try:
            account_info['latest_title'] = item.select('.sp-txt a')[0].text
            account_info['latest_link'] = item.select('.sp-txt a')[0]['href']
        except IndexError:
            pass
        search_list.append(account_info)
        #print(account_info)
    return search_list

def update_cookies():
    s = requests.Session()
    headers = {"User-Agent": UA}
    s.headers.update(headers)
    url = BASE_URL + '/weixin?query=123'
    r = s.get(url)
    if 'SNUID' not in s.cookies:
        p = re.compile(r'(?<=SNUID=)\w+')
        s.cookies['SNUID'] = p.findall(r.text)[0]
        suv = ''.join([str(int(time.time()*1000000) + random.randint(0, 1000))])
        s.cookies['SUV'] = suv
    return s.cookies


if __name__ == '__main__':
    open_id = 'oIWsFt3nvJ2jaaxm9UOB_LUos02k'
    #print(weixin_search('简书'))
    # cookies = update_cookies()
    t0 = time.time()
    # print(get_account_info(open_id,cookies=cookies))
    #print(weixin_search("简书",cookies))
    t1 = time.time()
    # print(parse_list(open_id))
    t2 = time.time()
    print(parse_essay('https://mp.weixin.qq.com/s?__biz=MzAwMDY5MjA5NQ==&mid=401664711&idx=1&sn=5b95ca49d3057663ecc1a6006d68566b&scene=0&key=710a5d99946419d923675f7382917be31afaaa07bce9d44418a1547e55e1b07b65fd273af792ebd4c2758f6845c35a50&ascene=0&uin=Nzg0NDEwNTgy&devicetype=iMac+MacBookPro11%2C3+OSX+OSX+10.11.1+build(15B42)&version=11020201&pass_ticket=ry6h7SJtBVqVAmgCrnGzdr5cP56vWaK9zjyOJv9OU9yJRM2TCXuo9jVkwSWB1KjZ'))
    t3 = time.time()
    print(t1-t0, t2-t1, t3-t2)