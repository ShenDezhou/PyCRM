# -*- coding: utf-8 -*-  
from lib.tornadotools.route import Route
from _base import BasePage, MgrPage, MgrHandler
from config import settings
import tornado.gen
import time, hashlib
from tornado.gen import coroutine, Return, Task
from tornado.web import asynchronous
from util.validation import is_valid_email, is_valid_phone, is_valid_password, is_valid_name, is_valid_number
from uimodules import *
from page_config import *
from lte_util import *
import page_config
import map_config
import auth
from auth import assert_mgr, assert_user, preassert_user
import tornado.httpclient
import urllib
import json, random
import qrcode
from config_web import settings
from util import dump_json
import datetime
import copy
from lib import html2text
from mgr import *
from os.path import join, getsize
from copy import deepcopy

def get_duohero_page_routes():
    return [('/(' + '|'.join([x['id'] for x in DUOHERO_PAGES]) + ')', DuoHeroMainPage)] 

@Route(r"/duohero")
@Route(r"/duohero/(.*)")
class DuoHeroMainPage(BasePage):
    @coroutine
    def get(self, entry='console'):
       
        # entry = entry or 'console'
        ctx = {}
        if entry == 'console':
            pass

        page = get_duohero_page_by_entry(entry)
        self.render(page['layout'],
                    user=None,
                    entry=entry,
                    page=page,
                    page_config=map_config,
                    context=ctx)



@Route(r"/rest/duohero/(duohero|level)")
class _(BasePage):
    @coroutine
    def get(self,entry):
        print entry
        profile = yield self.fetchone_db("select st_value from t_settings where st_id=%s",entry)
        print profile
        self.write(profile['st_value'])

@Route(r"/rest/duohero/(duohero|level)/commit")
class _(BasePage):
    @coroutine
    def post(self,entry):
        comments_args = self.get_args({
            'st_value': '*'
        })
        if not comments_args:
            yield self.error('*标识为必填项')
            return
        yield self.update_db_by_obj("t_settings",comments_args,"st_id='%s'" % entry)
        yield self.restful({
            "message":"提交成功"
            })