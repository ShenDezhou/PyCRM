# -*- coding: utf-8 -*- 

import tornado.web
import os
import sys
sys.path.insert(0, "..")

from page_config import *




class ConsoleLoginEntry(tornado.web.UIModule):
    def css_files(self):
        return self.page['css'] if 'css' in self.page else []

    def javascript_files(self):
        return self.page['js'] if 'js' in self.page else []

    def embedded_javascript(self):
        return []

    def render(self, entry, page):
        self.page = page
        return self.render_string(self.page['tpl'])

class CommonMainEntry(tornado.web.UIModule):
    def css_files(self):
        return self.page['css'] if 'css' in self.page else []

    def javascript_files(self):
        return self.page['js'] if 'js' in self.page else []

    def embedded_javascript(self):
        content = self.page['embedded_js'] if 'embedded_js' in self.page else ''
        return content

    def render(self, entry, page, page_config, context = None):
        self.page = page
        return self.render_string(self.page['tpl'], page_config = page_config, context = context, entry = entry, page = page)

class ConsoleHeaderEntry(tornado.web.UIModule):
    """docstring for ConsoleHeaderEntry"""
    def render(self, entry, page):
        return self.render_string('console_header.html', page = page)

class ConsoleHeaderMenuEntry(tornado.web.UIModule):
    """docstring for ConsoleHeaderEntry"""
    def render(self, page):
        if 'menu' in page:
            return self.render_string(page['menu'])
        else:
            return ''

class ConsoleMainEntry(tornado.web.UIModule):
    def css_files(self):
        return self.page['css'] if 'css' in self.page else []

    def javascript_files(self):
        return self.page['js'] if 'js' in self.page else []

    def embedded_javascript(self):
        return []

    def render(self, entry, page, page_config, mgr):
        self.page = page
        return self.render_string(self.page['tpl'], page = page, page_config = page_config, mgr = mgr)

