# encoding: utf-8

# System
import os.path
import tornado.auth
import tornado.escape
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
from tornado.options import define, options
# Custom
import pyorient
import json
import re
from bs4 import BeautifulSoup
# Config
import env

define("port", default=8888, help="main server here", type=int)

ESCAPE_MAP = {'\0': '\\0', '\n': '\\n', '\r': '\\r', '\032': '\\Z',
              '\'': '\\\'', '"': '\\"', '\\': '\\\\'}
ESCAPE_REGEX = re.compile('[' + re.escape(''.join(ESCAPE_MAP.keys())) + ']')


def escape_string(value):
    return ("%s" % (ESCAPE_REGEX.sub(
        lambda match: ESCAPE_MAP.get(match.group(0)), value),))


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", MainHandler),
            (r"/article/([0-9]+)", ArticleHandler),
            (r"/article/view/([0-9]+)", MoreArticleHandler),
            (r"/keyword", KeywordHandler)
        ]
        settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), env.template_path),
            static_path=os.path.join(os.path.dirname(__file__), env.static_path),
            debug=env.debug,
        )
        tornado.web.Application.__init__(self, handlers, **settings)


class MainHandler(tornado.web.RequestHandler):
    # 连接到数据库
    def initialize(self):
        self.database = pyorient.OrientDB(env.DB_HOST, env.DB_PORT)
        self.database.connect(env.DB_USER, env.DB_PASS)
        if self.database.db_exists(env.DB_NAME, pyorient.STORAGE_TYPE_LOCAL):
            self.database.db_open(env.DB_NAME, env.DB_USER, env.DB_PASS)
        else:
            print "数据库打开失败"
            self.finish()

    # 获取文章列表(限制10篇)
    def get(self):
        query = "SELECT id, title, save_path, date FROM v_article ORDER BY date DESC LIMIT 10"
        result = self.database.query(query)
        if not result:
            self.send_error(500)
            return

        articles = list()
        for r in result:
            articles.append({
                'link': '/article/' + r.id,
                'src': '/static/' + r.save_path + '/1.jpg',
                'title': r.title,
                'desc': '发布日期: ' + r.date
            })
        self.render("index.html", articles=articles, offset=10)

    # 断开数据库连接
    def on_finish(self):
        self.database.db_close()


class ArticleHandler(tornado.web.RequestHandler):
    # 连接到数据库
    def initialize(self):
        self.database = pyorient.OrientDB(env.DB_HOST, env.DB_PORT)
        self.database.connect(env.DB_USER, env.DB_PASS)
        if self.database.db_exists(env.DB_NAME, pyorient.STORAGE_TYPE_LOCAL):
            self.database.db_open(env.DB_NAME, env.DB_USER, env.DB_PASS)
        else:
            print "数据库打开失败"
            self.finish()

    def get(self, article_id):
        # 处理文章页面
        with open('static/storage/article_' + article_id + "/content.html", "r") as f:
            html = f.read()
            soup = BeautifulSoup(html, 'lxml', from_encoding='utf-8')
        # --- Title of article ---
        title = soup.find(name="h2", attrs={'id': 'activity-name'})
        if title is not None:
            title = title.string.strip()
        else:
            title = "阅读文章"
        # --- Content of article ---
        content = soup.find(name="div", attrs={'id': 'js_content'})
        imgs = content.findAll(name='img')
        for img in imgs:
            img.attrs['src'] = '/static/storage/article_' + article_id + '/' + img['src']

        # 获取已有关键词
        query = "SELECT name FROM (SELECT EXPAND(OUT()) FROM v_article WHERE id = '{}')".format(article_id)
        result = self.database.query(query)
        keywords = list()
        for r in result:
            keywords.append(r.name)

        self.render("article.html", id=article_id, title=title, content=content, keywords=keywords)

    # 断开数据库连接
    def on_finish(self):
        self.database.db_close()


class KeywordHandler(tornado.web.RequestHandler):
    # 连接到数据库
    def initialize(self):
        self.database = pyorient.OrientDB(env.DB_HOST, env.DB_PORT)
        self.database.connect(env.DB_USER, env.DB_PASS)
        if self.database.db_exists(env.DB_NAME, pyorient.STORAGE_TYPE_LOCAL):
            self.database.db_open(env.DB_NAME, env.DB_USER, env.DB_PASS)
        else:
            print "数据库打开失败"
            self.finish()

    # 添加文章关键字
    def post(self):
        article_id = self.get_argument('article_id').encode('utf-8')
        keyword = self.get_argument('keyword').encode('utf-8')
        keyword = escape_string(keyword)

        # 确定此关键词是否在文章中
        query = "SELECT 1 FROM v_article WHERE text LIKE '%{0}%' AND id = '{1}'".format(keyword, article_id)
        if not self.database.query(query):
            self.send_error(404)
            return

        # 确定关键词是否已存在于图库中
        query = "SELECT @rid FROM v_tag WHERE name = '{}'".format(keyword)
        result = self.database.query(query)
        if not result:
            query = "INSERT INTO v_tag (name) VALUES ('{}')".format(keyword)
            self.database.command(query)
            query = "SELECT @rid FROM v_tag WHERE name = '{}'".format(keyword)
            result = self.database.query(query)

        # 建立关键词与文章的联系
        query = "CREATE EDGE e_has_tag FROM (SELECT FROM v_article WHERE id = '{0}') TO {1}".format(
            article_id, result[0].rid
        )
        if self.database.command(query):
            self.write('success')
        else:
            self.send_error(500)

    # 删除文章关键字
    def delete(self):
        article_id = self.get_argument('article_id').encode('utf-8')
        keyword = self.get_argument('keyword').encode('utf-8')
        keyword = escape_string(keyword)

        query = "SELECT @rid FROM v_tag WHERE name = '{}'".format(keyword)
        result = self.database.query(query)
        if not result:
            self.send_error(404)
        query = "DELETE EDGE e_has_tag FROM (SELECT FROM v_article WHERE id = '{0}') TO {1}".format(
            article_id, result[0].rid
        )
        if self.database.command(query):
            self.write('success')
        else:
            self.send_error(500)

    # 断开数据库连接
    def on_finish(self):
        self.database.db_close()


class MoreArticleHandler(tornado.web.RequestHandler):
    # 连接到数据库
    def initialize(self):
        self.database = pyorient.OrientDB(env.DB_HOST, env.DB_PORT)
        self.database.connect(env.DB_USER, env.DB_PASS)
        if self.database.db_exists(env.DB_NAME, pyorient.STORAGE_TYPE_LOCAL):
            self.database.db_open(env.DB_NAME, env.DB_USER, env.DB_PASS)
        else:
            print "数据库打开失败"
            self.finish()

    # 文章数据
    def get(self, offset):
        query = "SELECT id, title, save_path, date FROM v_article ORDER BY date DESC LIMIT 10 SKIP {}".format(offset)
        result = self.database.query(query)
        if not result:
            self.send_error(500)
            return

        articles = list()
        for r in result:
            articles.append({
                'link': '/article/' + r.id,
                'src': '/static/' + r.save_path + '/1.jpg',
                'title': r.title,
                'desc': '发布日期: ' + r.date
            })
        self.write(json.dumps(articles))

    # 断开数据库连接
    def on_finish(self):
        self.database.db_close()


def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == '__main__':
    main()

