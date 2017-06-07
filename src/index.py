#!/usr/bin/python
# -*- coding: utf-8 -*-  
import tornado.ioloop
import tornado.web
import tornado.autoreload
from tornado.httpserver import HTTPServer
from tornado.options import define, options, parse_command_line
from lib.tornadotools.route import Route

from views.frontend import *
from views.rest import *
from views.frontend.page import *
from views.page import *
from views.corp_page import *
from views.duohero import *
from views.mgr import *
from util import session
from config import settings
import socket


# 使得 sys.getdefaultencoding() 的值为 'utf-8'  
reload(sys)                      # reload 才能调用 setdefaultencoding 方法  
sys.setdefaultencoding('utf-8')  # 设置 'utf-8'  


class Application(tornado.web.Application):
    def __init__(self, handlers=None, default_host="", transforms=None,
                 **settings):

        tornado.web.Application.__init__(self, handlers, default_host, transforms, **settings)
        self.session_manager = \
            session.SessionManager(settings["session_secret"], settings["store_options"], settings["session_timeout"])


application = Application(
    Route.routes() + 
    get_mgr_page_routes() + get_duohero_page_routes() + [
    (r"/(.*)", NotFoundPage),
], **settings)


define('port', default=8888, group='application')

if __name__ == "__main__":      
    parse_command_line()  
    print "Application starts on port: ", options.port
    #application.listen(options.port)
    http_server = HTTPServer(application, xheaders=True)
    http_server.listen(options.port)

    print "Production: ", settings['production']
    print "Debug: ", settings['debug']
   
    if settings['debug']:
        tornado.autoreload.start()
        for dir, _, files in os.walk('./'):
            [tornado.autoreload.watch(dir + '/' + f) for f in files if not f.startswith('.')]


    tornado.ioloop.IOLoop.instance().start()
