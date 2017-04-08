#-*- coding:utf-8 -*-
from lib.tornadotools.route import Route
from _base import MgrHandler, genenate_file_key
from page import get_survey
from config import settings
from tornado.gen import coroutine, Return
from tornado.web import asynchronous
import auth
from auth import assert_mgr, assert_user
from auth import assert_mgr
from lte_util import *
import json
import time
import re, os
import config
from util import dump_json
from util import read_file, write_file, get_or_create_path
from util.send_phone_email import send_email, send_message, send_more_email
from util.encrypt import encrypt_pwd
from util.validation import *
import datetime
import tornado.httpclient
import urllib
import json
import qrcode
from lib import weixin_sogou
import short_url
import logging
from auth import is_role_in
import re

@Route(r"/unit/test")
class _(MgrHandler):
    @coroutine
    def get(self):
        org_member = yield self.query_db(
            "select code_name from t_codes where code_type='member_type' and code_id like '%%org%%'")
        normal_member = yield self.query_db(
            "select code_id from t_codes where code_type='member_type' and code_id not like '%%advanced%%'")
        print(type(org_member))
        print(org_member)
        normal_member_list = [x['code_id'] for x in normal_member]
        print("#"*10,'normal_member',normal_member_list)
        org_member_list = [x['code_name'] for x in org_member]
        print org_member_list
        for member in org_member:
            if member['code_name'] in (u"企业普通会员",u"企业理事会员"):
                print("cool")
            else:
                print("not cool")
        self.restful({
            "message" : 'cool!'
        })


#理事会员名单
@Route(r"/advanced/member/list")
class _(MgrHandler):

    @coroutine
    def get(self, *args, **kwargs):
        advanced_org_member = yield self.query_db("""select DISTINCT o.org_name,case when p.gender = 1 then '男' else '女' end as gender,p.cellphone,p.email,concat('&nbsp',p.fullname,'&nbsp&nbsp')as fullname from t_person as p
                    left join t_org_person as op
                    on op.person_id = p.person_id
                    left join t_member as m
                    on m.org_id = op.org_id
                    left join t_org as o
                    on o.org_id = op.org_id
                    where op.is_primary = 1 and m.status = 'valid'
                    and m.member_type = 'advanced_org_member' order by o.org_name""")

        advanced_member = yield self.query_db("""select DISTINCT o.org_name,case when p.gender = 1 then '男' else '女' end as gender,p.cellphone,p.email,concat('&nbsp',p.fullname,'&nbsp&nbsp&nbsp')as fullname from t_person as p
                    left join t_org_person as op
                    on op.person_id = p.person_id
                    left join t_member as m
                    on m.person_id = op.person_id
                    left join t_org as o
                    on o.org_id = op.org_id
                    where m.status = 'valid'
                    and m.member_type = 'advanced_member' order by o.org_name""")
        org_table = ''
        table = ''
        org_count = 0
        count = 0
        for m in advanced_org_member:
            org_count += 1
            org_table += '<tr><th>%s</th><th>%s</th><th>%s</th><th>%s</th><th>%s</th></tr>' % (m['fullname'], m['gender'], m['cellphone'], m['email'], m['org_name'])

        for m in advanced_member:
            count += 1
            table += '<tr><th>%s</th><th>%s</th><th>%s</th><th>%s</th><th>%s</th></tr>'%(m['fullname'],m['gender'],m['cellphone'],m['email'],m['org_name'])
        self.write("""
        <div style="font-size: 100px;;width:1000px;font-family:'SimSun';">
        <hr>
        <table style="text-align: left;" border='1'>
        <caption>企业理事会员名单({org_count} 人)</caption>
        <tr>
        <th>姓名</th>
        <th>性别</th>
        <th>手机</th>
        <th>邮箱</th>
        <th>公司</th>
        </tr>
        {org_table}
        </table>
        <hr>
        <table style="text-align: left" border='1'>
        <caption>个人理事会员名单({count} 人)</caption>
        <tr>
        <th>姓名</th>
        <th>性别</th>
        <th>手机</th>
        <th>邮箱</th>
        <th>公司</th>
        </tr>
        {table}
        </table>
        </div>""".format(org_count=org_count,org_table=org_table,count=count,table=table))
        self.finish()


#
@Route(r"/member/profile")
class _(MgrHandler):
    @coroutine
    def get(self):
        res = yield self.fetchone_db(
            """select code_id from t_codes where code_type = 'member_fee' and code_name = 'weixin_group'""")
        member_fee = res['code_id']
        print (type(int(member_fee)))
        person_id = '8a19cd5b-53a7-4549-b7df-6c02083294b4'
        member = yield self.query_db("""(select t.* , c.code_name as member_type_name
                                                            from t_member as t
                                                            left join t_codes as c
                                                            on c.code_id = t.member_type
                                                            where t.person_id=%s)
                                                            UNION
                                                            (select t.* ,c.code_name as member_type_name from t_org_person as op
                                                            left join t_member as t
                                                            on op.org_id = t.org_id
                                                            left join t_codes as c
                                                            on c.code_id = t.member_type
                                                            where op.is_primary = 1
                                                            and op.person_id = %s)""",person_id,person_id)

        print(member)