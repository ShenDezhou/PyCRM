# -*- encoding=utf-8 -*-

# System
import random
import time
import logging
# Custom
import pyorient
# Config
import env

logger = logging.getLogger('Crawler')
null_proxy = {}


# 从数据库中随机获得一个可靠的代理地址
def get():
    db = pyorient.OrientDB(env.DB_HOST, env.DB_PORT)
    db.connect(env.DB_USER, env.DB_PASS)
    if db.db_exists(env.DB_NAME, pyorient.STORAGE_TYPE_LOCAL):
        db.db_open(env.DB_NAME, env.DB_USER, env.DB_PASS)
    else:
        logger.error('DB connection failure.')
        return False

    query = 'SELECT host, port, protocol, usage_count FROM v_proxy ORDER BY usage_count ASC LIMIT 1'
    result = db.query(query)
    db.db_close()
    if not result:
        logger.warn('No proxy found.')
        return False
    else:
        host = result[0].host
        port = result[0].port
        protocol = result[0].protocol
        proxy = dict(
            host=host,
            port=str(port),
            protocol=protocol.lower()
        )
        return proxy


# 随机抽取一个User Agent作为爬虫使用
def get_user_agent():
    ua = [
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
        "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5",
        "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24"
    ]
    return random.choice(ua)


# # 上报代理使用失败
# def failure(proxy):
#     db = pyorient.OrientDB(env.DB_HOST, env.DB_PORT)
#     db.connect(env.DB_USER, env.DB_PASS)
#     if db.db_exists(env.DB_NAME, pyorient.STORAGE_TYPE_LOCAL):
#         db.db_open(env.DB_NAME, env.DB_USER, env.DB_PASS)
#     else:
#         logger.warn('DB connection failure. Abandon aborted.')
#         return False
#
    # cmd = "UPDATE v_proxy INCREMENT usage_count = 1, failure_count = 1 WHERE host = '{0}' AND port = {}".format(
    #     proxy['host'], proxy['port']
    # )
#     db.command(cmd)
#     db.db_close()


# 丢弃不可用的代理
def abandon(proxy):
    db = pyorient.OrientDB(env.DB_HOST, env.DB_PORT)
    db.connect(env.DB_USER, env.DB_PASS)
    if db.db_exists(env.DB_NAME, pyorient.STORAGE_TYPE_LOCAL):
        db.db_open(env.DB_NAME, env.DB_USER, env.DB_PASS)
    else:
        logger.error('DB connection failure. Abandon aborted.')
        return False

    cmd = "DELETE VERTEX v_proxy WHERE host = '{0}' AND port = {1}".format(proxy['host'], proxy['port'])
    result = db.command(cmd)
    return result


# 将本次爬虫运行情况上报数据库
def report(proxy, start_time, end_time, url, page_type, is_ok):

    # 连接数据库
    db = pyorient.OrientDB(env.DB_HOST, env.DB_PORT)
    db.connect(env.DB_USER, env.DB_PASS)
    if db.db_exists(env.DB_NAME, pyorient.STORAGE_TYPE_LOCAL):
        db.db_open(env.DB_NAME, env.DB_USER, env.DB_PASS)
    else:
        logger.error('DB connection failure. Abandon aborted.')
        return False

    # 刷新代理统计信息
    if is_ok is False:
        cmd = "UPDATE v_proxy INCREMENT usage_count = 1, failure_count = 1 WHERE host = '{0}' AND port = {1}".format(
            proxy['host'], proxy['port']
        )
        db.command(cmd)
        return
    else:
        cmd = "UPDATE v_proxy INCREMENT usage_count = 1 WHERE host = '{0}' AND port = {1}".format(
            proxy['host'], proxy['port']
        )
        db.command(cmd)

    # 建立本次代理爬取报告
    cmd = '''INSERT INTO v_crawl_report (start_at, end_at, page_type, url, took_time)
               VALUES ({0}, {1}, "{2}", "{3}", {4})'''.format(
        start_time, end_time, page_type, url, end_time - start_time
    )
    db.command(cmd)
    query = "SELECT @rid FROM v_crawl_report WHERE url = '{0}' AND start_at = {1}".format(
        url, start_time
    )
    result = db.query(query)
    if result:
        cmd = 'CREATE EDGE e_has_report FROM (SELECT FROM v_proxy WHERE host = "{0}" AND port = {1}) TO {2}'.format(
            proxy['host'], proxy['port'], result[0].rid
        )
        db.command(cmd)
    else:
        logger.warn('Failed to create a proxy report.')
        return False

