# -*- coding: utf-8 -*-  
from lib.tornadotools.route import Route
from .._base import BasePage, MgrPage
from config import settings
import tornado.gen
import time, hashlib
from tornado.gen import coroutine, Return, Task
from tornado.web import asynchronous
from util.validation import is_valid_email, is_valid_phone, is_valid_password, is_valid_name ,is_valid_number
from ..uimodules import *
from ..page_config import *
from ..lte_util import *
from .. import page_config
from .. import map_config
from .. import auth
from ..auth import assert_mgr, assert_user, preassert_user
import tornado.httpclient
import urllib
import json, random
import qrcode
from config_web import settings
from util import dump_json
import datetime
import copy
from lib import html2text


@Route(r"/home_test")
class _(BasePage):
    @coroutine
    def get(self):
        entry = 'home'
        ctx = {}
        ctx['events'] = yield self.query_db("""
                        select id, left(published,10) as published,title,pictures,data_source,
                                        activity_start_time, activity_end_time,
                                        activity_sponsor,activity_undertake,activity_place,general_place,
                                        DATE_FORMAT(activity_start_time, '%%Y年%%m月%%d日') as activity_start_date,
                                        DATE_FORMAT(activity_end_time, '%%Y年%%m月%%d日') as activity_end_date,
                                        DATE_FORMAT(activity_start_time, '%%H:%%i') as activity_start_hm,
                                        DATE_FORMAT(activity_end_time, '%%H:%%i') as activity_end_hm
                        from t_news 
                        where type='activity' and status = 'published' order by activity_start_time DESC limit 0, 8""")
        page = get_page_by_entry(entry)
        
        self.render(page['layout'], 
                    entry = entry,
                    page = page,
                    page_config = map_config,
                    context = ctx)


@Route(r"/datalab")
@Route(r"/datalab/")
class _(BasePage):
    @coroutine
    def do_filter(self,args):
        res= {}
        where = ''
        if args['data_type'] and args['data_type']!='None':
            where += "and d.data_type = '%s'" % args['data_type']
        res['result'] = yield self.query_db("select d.title,d.data_describle,d.id,d.org_name , t.tag_name as data_type ,d.org_describle ,d.pictures,d.industry,d.connect_person,d.connect_cellphone from t_dataset as d left join t_tag as t on t.tag_id = d.data_type where d.status='published' %s" % where)
        current_page = int(args['draw'])
        max_page = int(len(res) / 20 + (0 if len(res) % 20 == 0 else 1)) - 1
        if max_page < current_page:
            current_page = 0
        current_pages = range(max(0, current_page - 1), min(current_page + 1, max_page) + 1)
        start_pages = range(0, min(current_page, 3) + 1)
        end_pages = range(max(max_page - 3, current_page), max_page + 1)

        pagings = list(set(current_pages + start_pages + end_pages))
        pagings.sort()
        res['pagingIndexes'] = pagings
        res["currentPage"] = current_page
        res['maxPage'] = max_page
        res['minPage'] = 0
        res['data_type'] = args['data_type']
        raise Return(res)

    @coroutine
    def get(self):
        entry = 'datalab'
        args = self.get_args({
            'draw':0,
            'data_type':None
            })
        ctx = []
        ctx = yield self.do_filter(args)

        ctx['tag_type'] = yield self.query_db("select * from t_tag where tag_type='dataset_type' ")
        page = get_page_by_entry(entry)
        
        self.render(page['layout'], 
                    entry = entry,
                    page = page,
                    page_config = map_config,
                    context = ctx)


@Route(r"/page/datalab/(.*)")
class _(BasePage):
    @preassert_user
    @coroutine
    def get(self, id):
        entry = 'datalab_detail'
        page = get_page_by_entry(entry)
        context = {}
        context['datalab'] = yield self.fetchone_db("select d.org_type,d.attachments,d.content,d.org_name , t.tag_name as data_type ,d.org_describle ,d.pictures,d.industry,d.connect_person,d.connect_cellphone from t_dataset as d left join t_tag as t on t.tag_id = d.data_type where d.id=%s",id)
        self.render(page['layout'], 
                    entry = entry,
                    page = page,
                    page_config = map_config,
                    context = context)

