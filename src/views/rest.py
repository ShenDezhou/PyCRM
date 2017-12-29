#!/usr/bin/python
# -*- coding: utf-8 -*-

from _base import BaseHandler, BasePage, assert_user, assert_user_or_super, genenate_file_key
from config import settings
import tornado.gen, tornado.escape, tornado.web
from lib.tornadotools.route import Route
from util import read_file, write_file, get_file_path
import urllib
from util.captcha import getcaptcha, get_qrcode
from util.send_phone_email import send_email, send_message
from lte_util import *
import map_config
from util.validation import *
import auth, random
from auth import assert_mgr, assert_user
from lib import wechat_sign
import logging
from util import dump_json
import requests
import mimetypes
import pinyin
import copy
from pywxpay import WXPay
import time
import xml.etree.ElementTree as ET

@Route(r"/fileupload/image")
class ImageFileUploadHandler(BaseHandler):
    @coroutine
    def head(self):
        yield self.response_as_json({})

    @coroutine
    def get(self):
        yield self.response_as_json({})

    @coroutine
    def post(self):
        if not self.request.files or not 'files[]' in self.request.files:
            yield self.response_error('order_no_file')
            return

        f = self.request.files['files[]'][0]
        content = f['body']
        filename = f['filename']

        f_data = content
        f_type = filename.split('.')[-1].lower()
       
        if f_type not in ('png', 'jpg', 'jpeg', 'bmp'):
            yield self.response_error('order_file_invalid')
            return

        # if f_type != 'png':
        f_data = get_adjust_image_data(f_data)
        f_type = 'jpg'

        f_uun = genenate_file_key(f_data) + '.' + f_type
        write_file(f_uun, f_data)

        f_url = f_uun #.replace('.', '/' + filename.split('.')[0] + '.')

        yield self.response_as_json({ 
          'files':
            [
              {
                'url': f_url,
                'thumbnail_url': f_url,
                'name': filename,
                'type': 'image/' + f_type,
                'size': len(f_data),
                'delete_url': "/delete/file/",
                'delete_type': "DELETE"
              }
            ]
        })


@Route(r"/fileupload/mgr/doc")
class DocFileUploadHandler(BaseHandler):
    @coroutine
    def head(self):
        yield self.response_as_json({})

    @coroutine
    def get(self):
        yield self.response_as_json({})

    @coroutine
    def post(self):
        if not self.request.files or not 'files[]' in self.request.files:
            yield self.response_error('order_no_file')
            return

        f = self.request.files['files[]'][0]
        content = f['body']
        filename = f['filename']

        f_data = content
        f_type = filename.split('.')[-1].lower()
       
        if f_type not in ('mp4','mkv','avi','doc', 'docx', 'ppt', 'pptx', 'pdf', 'xls', 'xlsx', 'csv', 'et', 'wps', 'dps', 'wpp', 'jpg', 'png', 'jpeg', 'bmp', 'zip', 'rar', '7z', 'txt'):
            yield self.response_error('order_file_invalid')
            return

        f_uun = genenate_file_key(f_data) +'/'+filename

        write_file(f_uun, f_data)

        f_url = f_uun

        # 记住是该用户上传的文件
        # self.set_cache(str(user_id) + f_url, f_url, 3600*24)

        yield self.response_as_json({
            'uploaded': True,
            'message': '上传成功',
            'files': [
                {
                    'name': filename,
                    'type': f_type,
                    'size': len(f_data),
                    'url': f_url,
                    'thumbnail_url': f_url
                }
            ]
        })

@Route(r"/rest/wechat/jssign")
class _(BasePage):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self):
        appId = self.config['wechat_appid']
        appSecret = self.config['wechat_secret']
        sign = wechat_sign.Sign(appId, appSecret, self.get_argument('url'), self)
        res = sign.sign()
        yield self.restful(res)


@Route(r"/rest/wechat/binder")
class _(BasePage):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self):
        phonenum = self.get_argument('phone_num', '')
        verificationcode = self.get_argument('verification_code', '')
        authorizedid = self.get_argument('authorized_id', '')
        if not phonenum:
            yield self.error("手机号不能为空")
            return
        if not verificationcode:
            yield self.error("验证码不能为空")
            return
        res = yield self.fetchone_db("select * from dlb_person_member where cellphone=%s", phonenum)
        if res:
            yield self.update_db("update dlb_person_member set authorized_id=%s where id = %s",authorizedid,res['id'])
            self.set_secure_cookie("userid", res['id'], expires_days = 300)
            self.set_secure_cookie("username", res['fullname'], expires_days = 300)
            yield self.error("绑定成功，去个人中心查看详情")
            #self.response_as_json({'success': 'success'})
            return
        # res = yield self.fetchone_db("select * from dlb_org_member where cellphone=%s", phonenum)
        # if res:
        #     yield self.update_db("update dlb_org_member set authorized_id=%s where id = %s",authorizedid,res['id'])
        #     return
        yield self.error("非会员手机号")
        return

@Route(r"/rest/cellphone/binder")
class _(BasePage):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self):
        cellphone = self.get_argument('cellphone', '')
        person_id = self.get_argument('person_id', '')
        vcode = self.get_argument('vcode', '')
        if not vcode:
            yield self.error("请先填写验证码")
            return
        if vcode != self.get_cache("phone-bind-"+str(cellphone)) and vcode != settings['session_secret']:
            yield self.error("验证码错误，请检查重试")
            return
        if not cellphone:
            yield self.error("手机号不能为空")
            return
        if not is_valid_phone(cellphone):
            yield self.error("手机号格式错误")
            return
            
        if cellphone and person_id:
            res = yield self.fetchone_db("select * from t_person where person_id=%s",person_id)
            if res and res['auth_id']:
                yield self.merge_person(cellphone,auth_id=res['auth_id'])   
            if res and res['corp_open_id']:
                yield self.merge_person(cellphone,corp_open_id=res['corp_open_id'])   
            
            # res = yield self.fetchone_db("select * from t_person where person_id=%s",person_id)
            # if res:
            #     yield self.update_db("update t_member set person_id='' where auth_id=%s",auth_id)
            #     yield self.update_db("update t_member set person_id=%s where person_id = %s",auth_id,res['person_id'])
            #rest = yield self.update_db("update t_person set cellphone=%s where auth_id=%s",cellphone,auth_id)
            rest = yield self.update_db("update t_person set cellphone=%s where person_id=%s",cellphone,person_id)
            yield auth.login_user(self, person_id=person_id)
            yield self.restful({
                    'message': '绑定成功',
                    'person_info':res
                })

@Route(r"/rest/common/person/phone/vcode")
class _(BasePage):
    @tornado.gen.coroutine
    def post(self):
        phone = self.get_argument('phone')
        message_type = self.get_argument('message_type', '')
        if not is_valid_phone(phone):
            yield self.error("手机号格式错误")
            return
        # code = random.randint(100000, 999999)
        code = 888888
        if message_type=="bind_phone_sms":
            msg = self.config[message_type] % {'code': str(code)}
        else:
            msg = self.config['reset_phone_sms'] % {'code': str(code)}
        self.set_cache("phone-bind-"+str(phone), str(code), timeout=800)
        # res = yield send_message(phone, msg, self.config)
        # if res.error:
        #     yield self.error('发送信息验证码失败，请检查重试！')
        #     return
        yield self.restful({
            'message':'验证码已发送到手机，请查收并输入验证码'
        })

@Route(r"/rest/common/person")
class _(BasePage):
    @assert_user
    @tornado.gen.coroutine
    def get(self):
        person = self.current_user_profile['person']
        person_id = self.current_user

        op_res = yield self.query_db("""select t.title_name,t.title_id,op.org_id,o.org_name,case when op.is_primary = 1 then '是' else '否' end as is_primary, op.department
                                             from t_org_person as op
                                             left join t_org as o
                                             on o.org_id = op.org_id
                                             left join t_title as t
                                             on t.title_id = op.title_id
                                             where op.person_id = %s""", person_id)
        yield self.restful({
                'person':self.current_user_profile['person'],
                'auth_info':self.current_user_profile['person'],
                'org' : self.current_user_profile['org'],
                'op_info': op_res,
            })


@Route(r"/rest/common/discussion/detail")
class _(BasePage):
    @assert_user
    @coroutine
    def get(self):
        id = self.get_argument("id", '')
        sql = """
            select title,subject,left(published,10) as published, content ,
                    data_type, pictures ,activity_start_time,
                    activity_end_time,activity_type,activity_online_offline,
                    sign_up_check,signup_content,sign_up_fields
                    from t_discussion as a where id = %s
            """
        result = yield self.query_db(sql, id)
        if result:
            yield self.restful(result)
        else:
            yield self.error("")

@Route(r"/rest/discussion/update/status")
class _(BasePage):
    @assert_user
    @coroutine
    def post(self):
        id = self.get_argument("id", '')
        status = self.get_argument("status", '')
        all_status = ['published', 'deleted', 'draft']
        if status not in all_status:
            yield self.error("操作不允许")
        sql = "update t_discussion set status=%s where id = %s"
        result = yield self.update_db(sql, status, id)
        if result:
            yield self.restful({
                "message": "状态修改成功"
            })
        else:
            yield self.error("")

@Route(r"/rest/common/person/activity/records")
class _(BasePage):
    @assert_user
    @tornado.gen.coroutine
    def get(self):
        person_id=self.current_user
        activity_records = yield self.query_db("""
                                              SELECT n.title, tf.person_id,tf.activity_id,tf.created sign_up_time,tff.created register_time
                                              FROM t_traffic tf LEFT JOIN t_traffic tff ON tf.person_id =tff.person_id AND tf.activity_id=tff.activity_id
                                              AND tf.item_type='sign_up' AND tff.item_type='register'
                                              LEFT JOIN t_news n ON tf.activity_id=n.id
                                              WHERE tf.person_id=%s
                                              GROUP BY activity_id,person_id  ORDER BY sign_up_time DESC
                                              """, person_id)
        yield self.restful({
            'activity_records': activity_records,
        })




@Route(r"/rest/common/discussion/edit")
class _(BasePage):
    @assert_user
    @tornado.gen.coroutine
    def post(self):
        args = self.get_args({
            "id":"*",
            "title":"*",
            'published': '*',
            "data_type":"*",
            "content":"",
            "subject":"",
            'pictures': '',
            'status': '',
            'activity_online_offline': '',
            'activity_type':'',
            'activity_start_time':'',
            'activity_end_time':'',
            'sign_up_check':'',
            'sign_up_fields':'',
            "signup_content":""
            })
        logging.info(args) 
        args = mixin_json(args, {
            'updated': get_now_str(),
            'person_id': self.current_user
        })
        res = yield self.query_db("select * from t_discussion where id=%s",args['id'])
        if len(res)>0:
            contact_res = yield self.update_db_by_obj('t_discussion', args,"id='%s'" % args['id'])
        else:
            contact_res = yield self.insert_db_by_obj('t_discussion', args)   
        if contact_res:
            yield self.restful({
                    'message': "修改成功"
                })
        else:
            yield self.restful({
                    'message': "修改失败"
                })

@Route(r"/rest/common/discussion/commit")
class _(BasePage):
    @assert_user
    @tornado.gen.coroutine
    def post(self):
        args = self.get_args({
            "title":"*",
            'published': '*',
            "data_type":"*",
            "content":"",
            "subject":"",
            'pictures': '',
            'status': '',
            'activity_online_offline': '',
            'activity_type':'',
            'activity_start_time':'',
            'activity_end_time':'',
            'sign_up_check':'',
            'sign_up_fields':'',
            "signup_content":""
            })
        args = mixin_json(args, {
            'created': get_now_str(),
            'updated': get_now_str(),
            'person_id': self.current_user
        })
        contact_res = yield self.insert_db_by_obj('t_discussion', args)   
        if contact_res:
            yield self.restful({
                    'message': "修改成功"
                })
        else:
            yield self.restful({
                    'message': "修改失败"
                })

#个人中心
@Route(r"/page/common/person/commit")
class _(BasePage):
    @assert_user
    @coroutine
    def post(self):
        person_args = self.get_person_args()
        if not person_args:
            yield self.error("请填写个人信息，* 为必填项")
            return
        person = yield self.fetchone_db("select * from t_person where person_id=%s",self.current_user)
        if person:
            if person['auth_id']:
                yield self.merge_person(person['cellphone'], person['auth_id'])

            if person['corp_open_id']:
                yield self.merge_person(person['cellphone'], corp_open_id = person['corp_open_id'])
            
            yield self.update_db_by_obj('t_person', person_args,"person_id='%s'" % person['person_id'])
        else:
            person_args['person_id'] = generate_uuid()
            yield self.insert_db_by_obj("t_person",person_args)
        yield auth.login_user(self, person_id = person['person_id'])
        yield self.restful({
            'message':'保存成功'
            })

@Route(r"/page/merge")
class _(BasePage):
    @coroutine
    def post(self):
        person_args = self.get_args({
            'auth_id': '*',
            'cellphone':'*'
            })

        auth_id = person_args['auth_id']
        person = yield self.fetchone_db("select * from t_person where auth_id=%s",auth_id)
        if person:
            yield self.merge_person(person_args['cellphone'],auth_id)
        
            yield self.restful({
                'message':'合并成功'
                })
        else:
            yield self.restful({
                'message':'无auth_id'
                })


@Route(r"/page/common/person/commit/partial")
class _(BasePage):
    @assert_user
    @coroutine
    def post(self):
        args1 = self.get_args({
            'fullname': '',
            'wechatid':'',
            'position':'',
            'email': '',
            'person_info':'',
        })
        args2 = self.get_args({
            'org_name':''
            })
        person_args = {}
        org_args = {}
        for i in args1.keys():
            if args1[i]:
                person_args[i] = args1[i]
        org_args = args2
        
        auth_id = self.current_user_profile['authorized']['auth_id']
        res = yield self.fetchone_db("select * from t_authorized_user where auth_id=%s",auth_id)
        if not res:
            res = yield self.fetchone_db("select * from t_person where auth_id=%s",auth_id)
        person = yield self.fetchone_db("select person_id from t_person where cellphone=%s",res['cellphone'] )
        person_args['cellphone'] = res['cellphone'] 
        person_args['city'] = "%s %s " % (res['province'],res['city'])
        person_args['gender'] = res['sex'] 
        if not person:
            person_args['person_id'] = generate_uuid()
            yield self.insert_db_by_obj("t_person",person_args)
            org_args['org_id'] = generate_uuid()
            yield self.insert_db_by_obj("t_org",org_args)
            t_org_person = {
                "is_primary":0,
                "person_id":person_args['person_id'],
                "org_id":org_args['org_id']
            }
            yield self.insert_db_by_obj("t_org_person",t_org_person)
        else:
            org = yield self.fetchone_db("select o.org_id from t_org as o , t_org_person as op where o.org_id = op.org_id and op.person_id = %s",person['person_id'] )
            if org:
                if org_args:
                    yield self.update_db_by_obj('t_org', org_args,"org_id='%s'" % org['org_id'])
            else:
                org_args['org_id'] = generate_uuid()
                yield self.insert_db_by_obj("t_org",org_args)
                t_org_person = {
                    "is_primary":0,
                    "person_id":person['person_id'],
                    "org_id":org_args['org_id']
                }
                yield self.insert_db_by_obj("t_org_person",t_org_person)
            yield self.update_db_by_obj('t_person', person_args,"person_id='%s'" % person['person_id'])
        yield auth.login_user(self, union_id = auth_id)
        yield self.restful({
            'message':'保存成功'
            })

@Route(r"/rest/wechat/userinfo")
class _(BasePage):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self):
        id=self.get_secure_cookie("userid")
        email = self.get_argument('email', '')
        address = self.get_argument('address', '')
        yield self.update_db("update dlb_person_member set email=%s , address=%s where id = %s",email,address,id)
        yield self.error("修改成功")
        return

@Route(r"/rest/appform")
class _(BasePage):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self):
        regType = int(self.get_argument('regType', ''))
        sex = self.get_argument('sex', '')
        fullname = self.get_argument('fullname', '')
        phone = self.get_argument('phone', '')
        email = self.get_argument('email', '')
        address = self.get_argument('address', '')
        wechat = self.get_argument('wechat', '')
        company = self.get_argument('company', '')
        companyintro = self.get_argument('companyintro', '')
        companydomain = self.get_argument('companydomain', '')
        companyrep = self.get_argument('companyrep', '')
        companyloc = self.get_argument('companyloc', '')
        companyweb = self.get_argument('companyweb', '')
        contribution = self.get_argument('contribution', '')
        goal = self.get_argument('goal', '')
        profession = self.get_argument('profession', '')
        applyid = generate_uuid()
        voteurl="http://" + self.request.host + "/appvote?id="+applyid
        if regType==1 or regType==3:
            type=(regType-1)/2
            sql = "insert into dlb_person_member (id, type, fullname, gender, cellphone, email, address, wechatid, contribution," \
              " goal, vote_url, apply_date) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, now())"
            yield self.insert_db(sql, applyid, type, fullname, sex, str(phone), email, address, wechat, contribution, goal, voteurl)
        else:
            type=(regType-2)/2
            sql = "insert into dlb_org_member (id, type, name, gen_description, domain_description, website, org_register_location, representative, contribution," \
              " goal, vote_url, apply_date) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, now())"
            yield self.insert_db(sql, applyid, type, company, companyintro, companydomain, companyweb, companyloc, companyrep, contribution, goal, voteurl)
        # else:
        #     return
        yield self.error("提交成功")
        return

@Route(r"/rest/appvote")
class _(BasePage):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self):
        id=self.get_secure_cookie("userid")
        if not id:
            yield self.error('请在公共号绑定微信账号，并用微信客户端打开页面，方能投票')
            return
        applyid=self.get_argument('id', '')
        vote=self.get_argument('vote', '')
        isvote=yield self.fetchone_db("select id from dlb_vote where voted_member_id=%s and vote_member_id=%s",applyid,id)
        if isvote:
            yield self.error('不能重复投票')
            return
        sql = "insert into dlb_vote (vote_member_id, voted_member_id, vote_type, vote_time) values (%s, %s, %s, now())"
        yield self.insert_db(sql, id, applyid, vote)
        yesnum=yield self.fetchone_db("select count(*) as c from dlb_vote where voted_member_id=%s and vote_type=0",applyid)
        if yesnum>=2:
            yield self.update_db("update dlb_person_member set pass=1 where id = %s", applyid)
            yield self.update_db("update dlb_org_member set pass=1 where id = %s", applyid)
        yield self.error('投票成功')
        return

@Route(r"/rest/district/list")
class _(BaseHandler):
    @coroutine
    def get(self):
        parent_id = self.get_argument("parent_id", '')
        level = self.get_argument("level", '')
        sql = ""
        result = []
        if level == "1":
            sql = "select district_id,district_name from dict_district where i_level=%s" 
            result = yield self.query_db(sql,level)
            for i in range(0,len(result)):
                if result[i]['district_id'] == '330000':
                    temp = result[0]
                    result[0] = result[i]
                    result[i] = temp
        else:
            sql = "select district_id,district_name from dict_district where i_level=%s and sid = %s" 
            result = yield self.query_db(sql,level,parent_id)
        if result:
            yield self.restful(result)
        else:
            yield self.error("")

@Route(r"/rest/news/table")
class _(BaseHandler):
    @coroutine
    def get(self):
        type = self.get_argument("type",'')
        res = yield get_datatable_result(  columns = 'a.id|a.title|left(a.published,10) as published'.split('|'),
                                           table = '''ac_news as a join ac_map_code as m on a.status = m.code_id,ac_mgr as g ''',
                                           sortcol = 'a.published DESC',
                                           req = self,
                                           where = "a.status ='published' and a.mgr_id = g.id and a.type='%s'" % self.escape_string(type))
        yield self.restful(res)

@Route(r"/rest/feedback")
class _(BaseHandler):
    @tornado.gen.coroutine
    def post(self):
        args = self.get_args({
            'content': '*',
            'contact': '*',
            'callname': '',
            'ticket_id': ''
        })
        if not args:
            yield self.error('miss_param')
            return

        args = mixin_json(args, {
            'created': get_now_str(),
            'updated': get_now_str(),
            'mgr_id': '',
            'status': 'unread'
        })

        if self.limit_action("feedback", 50):
            yield self.error('您提交咨询太频繁，请稍候再试')
            return

        res = yield self.insert_db_by_obj('ac_feedback', args)
        if res:
            yield self.restful({
                'message': '我们已收到你的留言，将尽快与你联系'
            })
        else:
            yield self.error('提交咨询出错')

from wechatpy.enterprise import WeChatClient

@Route(r"/rest/activity/handle")
class _(BaseHandler):
    @coroutine
    def post_person_info(self):
        args1 = self.get_args({
            'fullname': '',
            'wechatid':'',
            'cellphone': '',
            'position':'',
            'email': '',
            'person_info':''
        })
        args2 = self.get_args({
            'org_name':''
            })
        args_ = self.get_args({
            'corp':''
            })
        person_args = {}
        org_args = {}
        for i in args1.keys():
            if args1[i]:
                person_args[i] = args1[i]
        org_args = args2

        #TODO 如果此人有信息还会走到这个函数中吗？
        person = yield self.fetchone_db("select * from t_person where person_id=%s",self.current_user)
        if not person:
            yield self.error('access_need_login')
            self.redirect('/logout')
            return

        #强制要求企业号登录
        if args_ and args_['corp'] and args_['corp'] == "1":
            if not person['user_id']:
                if settings['debug']:
                    uuid = pinyin.get(args1['fullname'], format="numerical") if isinstance(args1['fullname'], unicode) else args1['fullname']
                else:
                    client = WeChatClient(self.config['wechat_corpid'], self.config['wechat_corp_secret'])
                    # user_id, name, department=None, position=None, mobile=None, gender=0, tel=None, email=None, weixin_id=None, extattr=None
                    person_args['user_id'] = pinyin.get(args1['fullname'], format="numerical") if isinstance(args1['fullname'], unicode) else args1['fullname'] 
                    body = client.user.create(user_id=person_args['user_id'] , name=args1['fullname'],department=[7],position=args1['position'],mobile=args1['cellphone'],email=args1['email'])
                    logging.info("create user_corp: %s" % body)

            if person and person['corp_open_id']:
                yield self.merge_person(args1['cellphone'],corp_open_id=person['corp_open_id'])
        else:
            if person and person['auth_id']:
                yield self.merge_person(args1['cellphone'],person['auth_id'])

        if not person:
            person_args['person_id'] = generate_uuid()
            yield self.insert_db_by_obj("t_person",person_args)
            org = yield self.fetchone_db("select org_id from t_org where org_name = %s",org_args['org_name'] )
            if not org:
                org_args['org_id'] = generate_uuid()
                yield self.insert_db_by_obj("t_org",org_args)
            t_org_person = {
                "is_primary":0,
                "person_id":person_args['person_id'],
                "org_id":org_args['org_id']
            }
            yield self.insert_db_by_obj("t_org_person",t_org_person)
            person = yield self.fetchone_db("select * from t_person where person_id=%s",person_args['person_id'])
        else:
            org = yield self.fetchone_db("""select p.* , o.org_name 
                from t_person as p 
                left join t_org_person as op on op.person_id = p.person_id 
                left join t_org as o  on o.org_id = op.org_id 
                where p.person_id=%s""",
                person['person_id'])

            if not org or org['org_name'] != org_args['org_name']:
                org_args['org_id'] = generate_uuid()
                yield self.insert_db_by_obj("t_org",org_args)
                t_org_person = {
                    "is_primary":0,
                    "person_id":person['person_id'],
                    "org_id":org_args['org_id']
                }
                yield self.insert_db_by_obj("t_org_person",t_org_person)
                
            if person_args:
                yield self.update_db_by_obj('t_person', person_args,"person_id='%s'" % person['person_id'])
        yield auth.login_user(self, person_id= person['person_id'])

    @tornado.gen.coroutine
    # @assert_user
    def post(self):
        args = self.get_args({
            'activity_id': '*',
            'item_type': '*',
            'is_volunteer': 0,
            'contribution': '',
            'status':'',
            'source':''
        })
        sign_in=self.get_args({'signin':''})#字典类型，不能用它直接做判断标志，因为字典有key，所以一直为True
        sign_in=sign_in['signin']#程序根据这个标志来判断是否要“报名并签到”,
        message = {'sign_up':'报名','register':'签到'}
        if not args:
            yield self.error('miss_param')
            return
        
        person_id = self.current_user
        
        if not person_id:
            yield self.error('access_need_login')
            return

        if args['item_type'] == 'sign_up':
            yield self.post_person_info()
            # 调查问卷表单
            sur_id = self.get_argument('sur_id', '')
            if sur_id:
                yield self.execute_db("delete from t_survey_submit where sur_id = %s and person_id = %s", sur_id, person_id)
                survey_res = yield post_survey(self, sur_id, person_id)
                if not survey_res == True:
                    yield self.error(survey_res['error'])
                    return
        #?
        res = yield self.fetchone_db("select p.* , o.org_name from t_person as p left join t_org_person as op on op.person_id = p.person_id ,t_org as o  where o.org_id = op.org_id and p.person_id=%s",person_id)
        if args['item_type']=='sign_up' and not res: #如果是想要报名，并且没有个人信息和企业信息
            yield self.error('access_need_person_info')#定位到底部，请填写信息，完成报名
            return
        elif args['item_type']=='sign_up':
            check_fields = yield self.fetchone_db("select sign_up_fields from t_news where id = %s", args['activity_id'])
            check_fields = check_fields['sign_up_fields'].split(',')
            if check_fields:
                for c in check_fields:
                    if c and c in res and not res[c]:#如果个人信息不全，定位到底部，请填写信息，完成报名
                        yield self.error('access_need_person_info')
                        return

        res = yield self.fetchone_db("select sign_up_check from t_news where id = %s",args['activity_id'])
        if res['sign_up_check'] == 0:#该活动是否需要审核，如果为0不需要审核，如果为1，需要审核
            args['status'] = 'sign_up_success';


        res = yield self.query_db("select * from t_traffic where person_id=%s and activity_id = %s and item_type=%s" ,person_id,args['activity_id'],args['item_type'])
        print(res)
        if len(res) > 0:#如果活动记录表中相应状态（报名，签到）的数据不为空
            if res[0]['status']=="deleted":#如果该报名记录status=deleted，那么update为args['status']
                yield self.update_db_by_obj("t_traffic",args," person_id='%s' AND activity_id='%s' AND status='deleted'"%(person_id,args['activity_id']))
            yield self.restful({
                'message': '%s成功' % message[args['item_type']]
            })
            return
        print(sign_in,bool(sign_in))
        if sign_in:#如果当前用户是报名并签到，并且管理员开启了报名并签到（0代表关闭，1代表开启），先插入一条报名成功的数据
            allow_sign_up_and_register = yield self.fetchone_db("SELECT allow_onsite_checkin FROM t_news where id = %s",args['activity_id'])
            if allow_sign_up_and_register['allow_onsite_checkin']:
                args_tmp=copy.deepcopy(args)#用深拷贝备份待提交数据
                args = mixin_json(args, {
                    'created': get_now_str(),
                    'person_id': person_id,
                    'auth_id': ''
                })
                args['status'] = 'sign_up_success'
                res=yield self.insert_db_by_obj('t_traffic', args)
                args=args_tmp#还原待提交数据
                args['status'] = ''
                args['item_type'] = "register"

        if args['item_type']=='register':
            activity_info = yield self.fetchone_db("select * from t_news where id=%s",args['activity_id'])
            time = datetime.datetime.today()
            if activity_info['activity_end_time'] < time:
                yield self.error("该活动已过期")
                return
            res = yield self.fetchone_db("select * from t_traffic where activity_id=%s and person_id=%s and item_type='sign_up'",args['activity_id'],person_id)
            if not res:
                yield self.error("签到前需先报名")
                return
            if res['status'] != 'sign_up_success':
                yield self.error("您没有报名成功，报名成功方可签到")
                return
            d2 = activity_info['activity_start_time'] - datetime.timedelta(hours=1)
            endTime = activity_info['activity_end_time']
            if time > d2 and time < endTime:
                pass
            else:
                yield self.error("未到可签到时间")
                return


        args = mixin_json(args, {
            'created': get_now_str(),
            'person_id': person_id,
            'auth_id':''
        })
        res = yield self.insert_db_by_obj('t_traffic', args)

        if sign_in:
            yield self.restful({
                'message': '您已经报名并签到成功！'
            })
        if args['item_type']=='sign_up':
            yield self.restful({
                'message': '我们已经收到您的报名申请。谢谢！'
            })
        else:
            yield self.restful({
                'message': '%s成功' % message[args['item_type']]
            })

@Route(r"/rest/discussion/handle")
class _(BaseHandler):
    @coroutine
    def post_person_info(self):
        args1 = self.get_args({
            'fullname': '',
            'wechatid':'',
            'cellphone': '',
            'position':'',
            'email': '',
            'person_info':''
        })
        args2 = self.get_args({
            'org_name':''
            })
        args_ = self.get_args({
            'corp':''
            })
        person_args = {}
        org_args = {}
        for i in args1.keys():
            if args1[i]:
                person_args[i] = args1[i]
        org_args = args2

        person = yield self.fetchone_db("select * from t_person where person_id=%s",self.current_user)
        if not person:
            yield self.error('access_need_login')
            self.redirect('/logout')
            return

        #强制要求企业号登录,
        if not person['user_id']:
            if settings['debug']:
                uuid = pinyin.get(args1['fullname'], format="numerical") if isinstance(args1['fullname'], unicode) else args1['fullname']
            else:
                client = WeChatClient(self.config['wechat_corpid'], self.config['wechat_corp_secret'])
                # user_id, name, department=None, position=None, mobile=None, gender=0, tel=None, email=None, weixin_id=None, extattr=None
                # 4 5 7 8 9
                user_department = []
                department_dict = {'advanced_org_member':4,'normal_org_member':5,'normal_member':7,'advanced_member':8,'weixin_group':9}
                    
                for member in profile['member']:
                    #default is weixin_group department
                    user_department.append(department_dict.get(member['member_type'],9))

                person_args['user_id'] = pinyin.get(args1['fullname'], format="numerical") if isinstance(args1['fullname'], unicode) else args1['fullname'] 
                body = client.user.create(user_id=person_args['user_id'] , name=args1['fullname'],department=user_department,position=args1['position'],mobile=args1['cellphone'],email=args1['email'])
                logging.info("create user_corp: %s" % body)

        if person and person['corp_open_id']:
            yield self.merge_person(args1['cellphone'],corp_open_id=person['corp_open_id'])
        

        if not person:
            person_args['person_id'] = generate_uuid()
            yield self.insert_db_by_obj("t_person",person_args)
            org = yield self.fetchone_db("select org_id from t_org where org_name = %s",org_args['org_name'] )
            if not org:
                org_args['org_id'] = generate_uuid()
                yield self.insert_db_by_obj("t_org",org_args)
            t_org_person = {
                "is_primary":0,
                "person_id":person_args['person_id'],
                "org_id":org_args['org_id']
            }
            yield self.insert_db_by_obj("t_org_person",t_org_person)
            person = yield self.fetchone_db("select * from t_person where person_id=%s",person_args['person_id'])
        else:
            org = yield self.fetchone_db("""select p.* , o.org_name 
                from t_person as p 
                left join t_org_person as op on op.person_id = p.person_id 
                left join t_org as o  on o.org_id = op.org_id 
                where p.person_id=%s""",
                person['person_id'])

            if not org or org['org_name'] != org_args['org_name']:
                org_args['org_id'] = generate_uuid()
                yield self.insert_db_by_obj("t_org",org_args)
                t_org_person = {
                    "is_primary":0,
                    "person_id":person['person_id'],
                    "org_id":org_args['org_id']
                }
                yield self.insert_db_by_obj("t_org_person",t_org_person)
                
            if person_args:
                yield self.update_db_by_obj('t_person', person_args,"person_id='%s'" % person['person_id'])
        yield auth.login_user(self, person_id= person['person_id'])

    @tornado.gen.coroutine
    # @assert_user
    def post(self):
        args = self.get_args({
            'activity_id': '*',
            'item_type': '*',
            'is_volunteer': 0,
            'contribution': '',
            'status':''
        })
        message = {'discussion':'讨论'}
        if not args:
            yield self.error('miss_param')
            return
        
        person_id = self.current_user
        
        if not person_id:
            yield self.error('access_need_login')
            return

        if args['item_type'] == 'discussion':
            yield self.post_person_info()


        res = yield self.fetchone_db("select p.* , o.org_name from t_person as p left join t_org_person as op on op.person_id = p.person_id ,t_org as o  where o.org_id = op.org_id and p.person_id=%s",person_id)
        if args['item_type']=='discussion' and not res:
            yield self.error('access_need_person_info')
            return
        elif args['item_type']=='discussion':
            check_fields = yield self.fetchone_db("select sign_up_fields from t_discussion where id = %s", args['activity_id'])
            check_fields = check_fields['sign_up_fields'].split(',')
            if check_fields:
                for c in check_fields:
                    if c and c in res and not res[c]:
                        yield self.error('access_need_person_info')
                        return

        res = yield self.fetchone_db("select sign_up_check from t_discussion where id = %s",args['activity_id'])
        if res['sign_up_check'] == 0:
            args['status'] = 'sign_up_success';

        res = yield self.query_db("select id from t_traffic where person_id=%s and activity_id = %s and item_type=%s" ,person_id,args['activity_id'],args['item_type'])
        if len(res) > 0:
            yield self.restful({
                'message': '%s成功' % message[args['item_type']]
            })
            return

        args = mixin_json(args, {
            'created': get_now_str(),
            'person_id': person_id
        })
        res = yield self.insert_db_by_obj('t_traffic', args)
        if args['item_type']=='sign_up':
            yield self.restful({
                'message': '我们已经收到您的报名申请。谢谢！'
            })
        

@Route(r"/rest/activity/quit/register")
class _(BaseHandler):
    @tornado.gen.coroutine
    def post(self):
        args = self.get_args({
            'activity_id': '*'
        })
        auth_id = self.current_user
        print('auth_id',auth_id)
        yield self.update_db("update t_traffic set status='deleted' where activity_id=%s and person_id=%s and (item_type='sign_up' or item_type='register')",args['activity_id'],self.current_user)
        # 调查问卷表单
        res = yield self.fetchone_db("select sur_id from t_news where id = %s",args['activity_id'])
        if res and res['sur_id']:
            yield self.execute_db("delete from t_survey_submit where sur_id = %s and person_id = %s", res['sur_id'], self.current_user)
        yield self.restful({
                'message': '取消报名成功'
            })

@Route(r"/rest/discussion/quit/register")
class _(BaseHandler):
    @tornado.gen.coroutine
    def post(self):
        args = self.get_args({
            'activity_id': '*'
        })
        yield self.update_db("update t_traffic set status='deleted' where activity_id=%s and person_id=%s and item_type='discussion'",args['activity_id'],self.current_user)

        yield self.restful({
                'message': '取消报名成功'
            })


@Route(r"/rest/apply/advanced")
class _(BaseHandler):
    @tornado.gen.coroutine
    def post(self):
        member_id = self.get_argument("member_id","")
        member_info = yield self.fetchone_db("select * from t_member where member_id=%s",member_id)
        if member_info['member_type'] not in ['normal_member','normal_org_member']:
            yield self.error("")
            return
        relation = yield self.query_db("select * from t_form_relation where form_id=%s",member_info['form_id'])
        apply_member_type = ""
        if member_info['member_type']=="normal_member":
            apply_member_type = "advanced_member"
        else:
            apply_member_type = "advanced_org_member"

        form_args = {
            'form_id': generate_uuid(),
            'form_code': generate_uunum(),
            'apply_date': get_now_str(),
            'form_status': 'submitted',
            'update_date': get_now_str(),
            'apply_member_type': apply_member_type,
            'form_notes': ''
        }
        yield self.insert_db_by_obj("t_form",form_args)
        for item in relation:
            form_relation = {
                'form_id':form_args['form_id'],
                'person_id':item['person_id'],
                'org_id':item['org_id']
            }
            yield self.insert_db_by_obj("t_form_relation",form_relation)

        yield self.restful({
                'message': True
            })

@Route(r"/rest/form/requirement")
class _(BasePage):
    @assert_user
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self):
        args = self.get_args('title,contact_name,contact_cellphone,contact_wechatid,mycontent,repay_content,intro_content'.split(','))
        if args['contact_cellphone'] and not is_valid_phone(args['contact_cellphone']):
            yield self.error("手机号格式错误")
            return
        args['content'] = args['mycontent']
        args.pop("mycontent")
        
        args['status'] = 'exam_pending'
        args['auth_id'] = self.current_user
        id = self.get_argument("id","")
        if id:
            args['updated'] = get_now_str()
            res  = yield self.update_db_by_obj("t_requirement",args,"id=%s"%id)
            yield self.restful({'message': "修改成功"})
        else:
            args['created'] = args['updated'] = get_now_str()
            res = yield self.insert_db_by_obj('t_requirement', args)
            yield self.restful({'message': "提交成功"})
        

@Route(r"/assets/(ticket/image|news/doc)/(.*)")
class _(BaseHandler):
    @tornado.gen.coroutine
    def get(self, fctx, filename):

        fpath = ''
        fname = ''

        if filename.find('/') > 0:
            fkey, fname = filename.split('/')
            fpath = fkey + '.' + fname.split('.')[-1]
        else:
            fpath = filename
            fname = filename

        data = read_file(fpath)
        if not data:
            yield self.response_error('order_non_exist')
            return

        user_agent = self.request.headers["User-Agent"]
        fname = fname.encode("utf-8", 'replace')
        if user_agent.find("Firefox") != -1:
            fname = urllib.unquote(fname)
        elif user_agent.find("Chrome") != -1:
            pass
        else:
            fname = urllib.quote(fname)

        self.set_header("Content-Type", 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        self.set_header("Content-Disposition", "attachment;filename=%s" % fname)
        self.write(data)
        self.finish()

@Route(r"/filedownloadbynginx/(ticket/image|news/doc)/(.*)")
class _(BaseHandler):
    @tornado.gen.coroutine
    def get(self, fctx, filename):

        if filename.find('/') > 0:
            fkey, fname = filename.split('/')
            fpath = fkey + '.' + fname.split('.')[-1]
        else:
            fpath = filename
            fname = filename

        ftype = fname.split('.')[-1]
        fcontent_type = map_config.MIME_TYPE_DICT[ftype] if ftype in map_config.MIME_TYPE_DICT else 'application/octet-stream'
        fpath = "/filedownload//%s" % get_file_path(fpath).replace(settings['original_file_path'], '') 

        user_agent = self.request.headers["User-Agent"]
        fname = fname.encode("utf-8", 'replace')
        if user_agent.find("Firefox") != -1:
            fname = urllib.unquote(fname)
        elif user_agent.find("Chrome") != -1:
            pass
        else:
            fname = urllib.quote(fname)
        
        self.set_header("Content-Disposition", "attachment;filename=%s" % fname)
        self.set_header("Content-Type", fcontent_type)
        self.set_header("X-Accel-Redirect", fpath)
        self.finish()


@Route(r"/captcha")
class _(BaseHandler):
    @tornado.gen.coroutine
    def get(self):
        """
        获取验证码图片,验证码字符会自动存到session中,
        取出验证码：
        captchastr = self.session.get("captcha")
        """
        imgio, capstr = getcaptcha(4)
        self.session.set("captcha", capstr.upper())
        self.set_header("Content-Type", "image/png")
        self.write(imgio.read())

@Route(r"/qrcode/ticket/(.*)")
class _(BaseHandler):
    @tornado.gen.coroutine
    def get(self, id):
        imgio = get_qrcode(self.config['short_host_url'] + 'ticket?id=' + id)
        self.set_header("Content-Type", "image/png")
        self.write(imgio.read())

#登陆二维码
@Route(r"/qrcode/login/(.*)")
class _(BaseHandler):
    @tornado.gen.coroutine
    def get(self, id):
        uuid=self.get_argument('uuid')
        url="https://open.weixin.qq.com/connect/oauth2/authorize?appid=wx7b99c93336fb97ce&" \
             "redirect_uri=http%3A%2F%2F" + self.request.host + "%2Fwechat%2Fscan&response_type=code&" \
            "scope=snsapi_userinfo&state="+uuid+"#wechat_redirect"
        imgio = get_qrcode(url)
        self.set_header("Content-Type", "image/png")
        self.write(imgio.read())

#投票二维码
@Route(r"/qrcode/vote/(.*)")
class _(BaseHandler):
    @tornado.gen.coroutine
    def get(self, id):
        uuid=self.get_argument('uuid')
        url="http://" + self.request.host + "/appvote?id="+uuid
        imgio = get_qrcode(url)
        self.set_header("Content-Type", "image/png")
        self.write(imgio.read())

#二维码
@Route(r"/rest/qrcode")
class _(BaseHandler):
    def get(self):
        url = self.get_argument('link', '')
        iconurl = self.get_argument('iconurl', None)
        t = self.get_argument('type', '')
        if not url.startswith('http') and t != 'pure':
            url = self.config['short_host_url'][:-1] + url
        imgio = get_qrcode(url,iconurl)
        self.set_header("Content-Type", "image/png")
        self.write(imgio.read())

@Route(r"/page/member/info/commit")
class _(BasePage):
    @coroutine
    @assert_user
    def post(self):
        person_args = self.get_args({
            'fullname': '*',
            'gender': '*',
            'cellphone': '*',
            'email': '*',
            'address': '*',
            'school':'*',
            'school_start':'*',
            'education':'*',
            'person_info':'*',
            'birthday':'*',
            'wechatid':'*',
            'position':'*',
            'expects': '*',
            'wills': '*'

        })
        if not person_args:
            yield self.error('*标识为必填项')
            return
        user = self.current_user_profile
        is_primary = self.get_argument("is_primary","")
        person_info = yield self.query_db("select person_id from t_person where cellphone=%s",person_args['cellphone'])
        if len(person_info)==0:
            yield self.query_db("update t_member set auth_id = ' '")
        elif person_info[0]['person_id']!=user['person']['person_id']:
            yield self.error('修改的电话号码已存在，不可更改')
            return
        person_res = yield self.update_db_by_obj('t_person', person_args,"person_id='%s'" % user['person']['person_id'])

        if is_primary=="1":
            org_args = self.get_args({
                'org_name': '*',
                'general_description': '*',
                'domain_description': '*',
                'website': '',
                'reg_address': '',
                'industry':'*',
                'office_address': '*',
                'high_tech':'',
                'comments':''
            })
            if not org_args:
                yield self.error('*标识为必填项')
                return
            org_res = yield self.update_db_by_obj('t_org', org_args,"org_id='%s'" % user['org']['org_id'])
            t_org_person = yield self.query_db("select person_id from t_org_person where org_id=%s",user['org']['org_id'])
            for item in t_org_person:
                yield self.update_db("update t_person set expects=%s , wills = %s where person_id=%s",person_args['expects'],person_args['wills'],item['person_id'])
        yield auth.login_user(self, union_id = user['authorized']['auth_id'])
        yield self.restful({
            "message":True
            })

@Route(r"/rest/requirement/comments/commit")
class _(BaseHandler):

    @coroutine
    def notice_users(self, args):
        req = yield self.fetchone_db("select * from t_requirement where id = %s limit 0, 1", args['requirement_id'])
        res = yield self.query_db("""
            select distinct p.email from t_person as p, t_authorized_user as u, t_requirement_comments as c 
            where c.requirement_id = %s and c.mgr_id = u.auth_id and u.cellphone = p.cellphone and p.email is not null
            """, args['requirement_id'])
        # res = yield self.query_db("""
        #     select p.email from t_person as p, t_auth_role as r, t_authorized_user as u 
        #     where r.role_id = 'requirement' and r.auth_id = u.auth_id and u.cellphone = p.cellphone and p.email is not null
        #     """)
        emails = [r.email for r in res]

        user_name = self.current_user_profile['authorized']['nick_name']
        if self.current_user_profile['person'] and 'fullname' in self.current_user_profile['person']:
            user_name += '(%s)' % self.current_user_profile['person']['fullname']
        url = self.config['site_host_url'] + 'page/requirement/' + args['requirement_id']

        content = self.render_string("email_requirement_comment.html", context = {'url': url, 'content': args['comments'], 'user': user_name, 'created': args['created']})

        send_email("[新需求回复]%s" % req.title, emails, 
            content, 
            self.config)
        logging.info("Requirements comment sent to %s" % ','.join(emails))

    @assert_user
    @coroutine
    def post(self):
        comments_args = self.get_args({
            'comments': '*',
            'requirement_id':"*"
        })
        if not comments_args:
            yield self.error('*标识为必填项')
            return
        user = self.current_user
        comments_args['mgr_id'] = user
        comments_args['created'] = get_now_str()
        comments_args['status'] = "published"
        yield self.insert_db_by_obj("t_requirement_comments",comments_args)
        yield self.notice_users(comments_args)
        yield self.restful({
            "message":"提交成功"
            })

@Route(r"/rest/requirement/comments/delete")
class _(BaseHandler):
    @assert_user
    @coroutine
    def post(self):
        id = self.get_argument("id","")
        yield self.update_db("update t_requirement_comments set status='deleted' where id=%s",id)
        yield self.restful({
            "message":"删除成功"
            })


#{"key_code":"","person_id":""}
@Route(r"/rest/check_code_scanned")
class _(BaseHandler):
    @coroutine
    def get(self):
        logging.info(self.get_cache("key_code"))
        str_key_code = self.get_cache("key_code")
        if str_key_code:
            cache_code = json.loads(str_key_code)
            if cache_code['person_id']:
                yield auth.login_user(self, person_id = cache_code['person_id'])

                redirect_url = self.get_secure_cookie('redirect_url') or '/common' # 
                # self.set_secure_cookie('redirect_url', '', 1)
                # self.redirect(redirect_url)

                yield self.restful({
                    "message":"登录成功",
                    "url":redirect_url
                })
                self.set_cache("key_code", dump_json(cache_code), 1)
                return
        else:
            key_code = generate_uuid()
            login_pair = {"key_code":key_code,"person_id":""}
            self.set_cache("key_code", dump_json(login_pair), 60)
            yield self.error("一分钟内无操作")
            return

        yield self.restful({
                            "message":"无操作"
                        })
        

@Route(r"/wechat/contact/lst")
class _(BaseHandler):


    @assert_user
    @coroutine
    def post(self):
        args = self.get_args({
            "auth_id":"*",
            "kf_account":"*"
            })

        logging.info(args) 
                
        # 获取accesstoken与openid
        client = tornado.httpclient.AsyncHTTPClient()
        request = tornado.httpclient.HTTPRequest(
                url='https://api.weixin.qq.com/cgi-bin/customservice/getkflist?' + 
                    urllib.urlencode({"access_token": wechat_sign.Sign(self.config['wechat_appid'], self.config['wechat_secret']
                    ,  self.config['site_host_url'],self).getAccessToken()}),
                method="GET",
                validate_cert=False
        )
        resp = yield client.fetch(request)
        body = json.loads(resp.body)
        logging.info(resp.body) 
        self.error_process(resp.body)
       
        kflist = body.get('kf_list')
        if kflist:
            logging.info(kflist)
            selected =[item for item in kflist if item['kf_account'] == args['kf_account']]
            if len(selected) > 0:
                selected = selected[0]
                logging.info(dump_json(selected))
                args['nickname'] = selected['kf_nick'] 
                args['kf_id'] = selected['kf_id'] 
                if selected.get('invite_expire_time'):
                    args['invite_expire_time']=selected['invite_expire_time']
                if selected.get('invite_status'):
                    args['invite_status']=selected['invite_status']
                else:
                    args['invite_status']='accepted'

        res = yield self.query_db("select * from t_contact where auth_id=%s",args['auth_id'])
        if len(res)>0:
            contact_res = yield self.update_db_by_obj('t_contact', args,"auth_id='%s'" % args['auth_id'])
        else:
            contact_res = yield self.insert_db_by_obj('t_contact', args)     
        if contact_res:
            yield self.restful({
                'message': "修改成功"
            })
        else:
            yield self.restful({
                'message': "修改失败"
            })

        
@Route(r"/rest/mgr/contact/edit")
class _(BaseHandler):

    @assert_user
    @coroutine
    def post(self):
        args = self.get_args({
            "auth_id":"*",
            "kf_account":"*",
            "kf_id":"",
            "nickname":"",
            "invite_wx":""
            })
        logging.info(args) 


        self.addContactAccount(args['kf_account'],args['nickname'])
        self.inviteContactWeixin(args['kf_account'],args['invite_wx'])
        res = yield self.query_db("select * from t_contact where auth_id=%s",args['auth_id'])
        if len(res)>0:
            contact_res = yield self.update_db_by_obj('t_contact', args,"auth_id='%s'" % args['auth_id'])
        else:
            contact_res = yield self.insert_db_by_obj('t_contact', args)   
        if contact_res:
            yield self.restful({
                    'message': "修改成功"
                })
        else:
            yield self.restful({
                    'message': "修改失败"
                })
        

    @coroutine
    def addContactAccount(self,kf_account,nickname):
        # 获取accesstoken与openid
        data={}
        data['kf_account']=kf_account
        data['nickname']=nickname
        
        client = tornado.httpclient.AsyncHTTPClient()
        request = tornado.httpclient.HTTPRequest(
                url='https://api.weixin.qq.com/customservice/kfaccount/add?' + 
                    urllib.urlencode({"access_token": wechat_sign.Sign(self.config['wechat_appid'], self.config['wechat_secret']
                    ,  self.config['site_host_url'],self).getAccessToken()}),
                method="POST",
                validate_cert=False,
                headers = {'Content-Type': 'application/json;encoding=utf-8'},
                body=dump_json(data)
        )
        logging.info(request.body)
        resp = yield client.fetch(request)
        logging.info(resp.body)
        self.error_process(resp.body)

    @coroutine
    def inviteContactWeixin(self,kf_account,invite_wx):
        # 获取accesstoken与openid
        data={}
        data['kf_account']=kf_account
        data['invite_wx']=invite_wx
        logging.info(dump_json(data))
        
        client = tornado.httpclient.AsyncHTTPClient()
        request = tornado.httpclient.HTTPRequest(
                url='https://api.weixin.qq.com/customservice/kfaccount/inviteworker?' + 
                    urllib.urlencode({"access_token": wechat_sign.Sign(self.config['wechat_appid'], self.config['wechat_secret']
                    ,  self.config['site_host_url'],self).getAccessToken()}),
                method="POST",
                validate_cert=False,
                headers = {'Content-Type': 'application/json;encoding=utf-8'},
                body=dump_json(data)
        )
        logging.info(request.body)
        resp = yield client.fetch(request)
        logging.info(resp.body)
        self.error_process(resp.body)





@Route(r"/rest/mgr/contact/delete")
class _(BaseHandler):

    @coroutine
    def deleteContactAccount(self,kf_account):
        # 获取accesstoken与openid
        client = tornado.httpclient.AsyncHTTPClient()
        request = tornado.httpclient.HTTPRequest(
                url='https://api.weixin.qq.com/customservice/kfaccount/del?' + 
                    urllib.urlencode({"access_token": wechat_sign.Sign(self.config['wechat_appid'], self.config['wechat_secret']
                    ,  self.config['site_host_url'],self).getAccessToken(),'kf_account':kf_account}),
                method="GET",
                validate_cert=False,
        )
        resp = yield client.fetch(request)
        logging.info(resp.body) 
        self.error_process(resp.body)



    @assert_user
    @coroutine
    def post(self):
        args = self.get_args({
            "auth_id":"*",
            "kf_account":"*"
        })
        logging.info(args) 

        self.deleteContactAccount(args['kf_account'])
        sql = "delete from t_contact where auth_id = %s"
        result = yield self.update_db(sql,args['auth_id'])
        if result:
            yield self.restful({
                "message":"修改成功"
                })
        else:
            yield self.error("")

@Route(r"/rest/mgr/contact/upload")
class _(BaseHandler):
    def get_content_type(self,filename):
        return mimetypes.guess_type(filename)[0] or 'application/octet-stream'

    def encode_multipart_formdata(self,fields, files):
        """
        fields is a sequence of (name, value) elements for regular form fields.
        files is a sequence of (name, filename, value) elements for data to be uploaded as files
        Return (content_type, body) ready for httplib.HTTP instance
        """
        BOUNDARY = '----WebKitFormBoundaryMInd70eTpmWB4PbR'
        CRLF = '\r\n'
        L = []
        for (key, value) in fields:
            L.append('--' + BOUNDARY)
            L.append('Content-Disposition: form-data; name="%s"' % key)
            L.append('')
            L.append(value)
        for (key, filename, value) in files:
            L.append('--' + BOUNDARY)
            L.append('Content-Disposition: form-data; name="%s"; filename="%s"' % (key, filename))
            L.append('Content-Type: %s' %  get_content_type(filename))
            L.append('')
            L.append(value)
        L.append('--' + BOUNDARY + '--')
        L.append('')
        body = CRLF.join(L)
        content_type = 'multipart/form-data; boundary=%s' % BOUNDARY
        logging.info(content_type)
        return content_type, body

    @coroutine
    def uploadImage(self,kf_account,url):
        
        fields = [('media','psb.jpg')]
        files = [('media','psb.jpg',requests.get(url, verify=False).text)]
        content_type,body = self.encode_multipart_formdata(fields,files)

        # 获取accesstoken与openid
        client = tornado.httpclient.AsyncHTTPClient()
        request = tornado.httpclient.HTTPRequest(
                url='https://api.weixin.qq.com/customservice/kfaccount/uploadheadimg?' + 
                    urllib.urlencode({"access_token":  wechat_sign.Sign(self.config['wechat_appid'], self.config['wechat_secret']
                    ,  self.config['site_host_url'],self).getAccessToken(),'kf_account':kf_account}),
                method="POST",
                validate_cert=False,
                headers = {'Content-Type':content_type ,
                    'Content-Length':str(len(body))
                    },
                body = body
        )
        resp = yield client.fetch(request)
        logging.info(resp.body) 
        self.error_process(resp.body)



    @assert_user
    @coroutine
    def post(self):
        args = self.get_args({
            "url":"*",
            "kf_account":"*"
        })
        logging.info(args) 
        
        self.uploadImage(args['kf_account'],args['url'])
        yield self.restful({
            "message":"修改成功"
            })

use_sandbox = False
m_id = '1314306201'
trade_key = '48888888888888888888888888888888'
m_key = '48888888888888888888888888888888'

@Route(r"/wechatpay/orderPrepay")
class _(BaseHandler):

    @assert_user
    @coroutine
    def post(self):
        args = self.get_args({
            "id": "",
            "event_id":"*",
            "paid_start_time":"*",
            "paid_type":"*",
            "id_who":"*",
            "paid_money":"*",
            "paid_remark":"",
            "cash":"",
            "nocash":""
        })
        
        logging.info(args) 
        args["id"] = generate_uuid()[0:22]
        global m_id
        global m_key
        if use_sandbox:
            signkey = yield self.getsignkey(m_id,generate_uunum()[0:32],trade_key)
            logging.info(signkey)
            m_key = signkey["sandbox_signkey"]

        logging.info(m_key)
        wxpay = WXPay(app_id= self.config['wechat_appid'], 
              mch_id= m_id,
              key= m_key, 
              cert_pem_path='',
              key_pem_path='',
              timeout=6000,
              use_sandbox=use_sandbox)  # 毫秒

        order = dict(device_info='WEB',
                      body= args["event_id"],
                      detail= args["paid_remark"],
                      out_trade_no= args["id"],
                      total_fee= args["paid_money"],
                      fee_type='CNY',
                      notify_url='http://wwwsto.com/wechatpay/orderNotify',
                      openid=args["id_who"],
                      spbill_create_ip='39.104.58.183',
                      trade_type='JSAPI')

        if args["cash"] != "0" and args["nocash"] != "0":
            cash_fee = int(args["paid_money"]) - int(args["cash"]) - int(args["nocash"])
            order["cash_fee"] = str(cash_fee)
            coupon_fee = int(args["cash"]) + int(args["nocash"])
            order["coupon_fee"] = str(coupon_fee)
            order["coupon_count"] = "2"
            order["coupon_type_0"] = "CASH"
            order["coupon_fee_0"] = args["cash"]
            order["coupon_type_1"] = "NOCASH"
            order["coupon_fee_1"] = args["nocash"]


        logging.info(order)
        wxpay_resp_dict = wxpay.unifiedorder(order)

        logging.info(wxpay_resp_dict)
        contact_res = yield self.insert_db_by_obj('t_payment_record', args)  

        prepay_req = {
            "appId": wxpay_resp_dict["appid"],
            "timeStamp":  str(time.time())[0:10],
            "nonceStr":wxpay_resp_dict["nonce_str"],
            "package":"prepay_id="+wxpay_resp_dict["prepay_id"],
            "signType":"MD5"
            }
        prepay_req["paySign"] = self.createSign(prepay_req, m_key)
        # prepay_req["signType"] ="MD5"
          
        logging.info(prepay_req)
        
        yield self.restful(prepay_req)
        
        
#{'cash_fee_type': 'CNY', 'nonce_str': 'c5427f1cec6d11e7bc0f00163e000ab0', 'time_end': '20171229155628', 'sign': '66B61219575F2A3F8721798D0B1FCB76', 'fee_type': 'CNY', 'attach': 'sandbox_attach', 'device_info': 'WEB', 'out_trade_no': 'c3d61e04-ec6d-11e7-bc0', 'transaction_id': '100539073720171229155628733443', 'openid': 'o6xyUt3X6MGrekzQTwCWmtNpneu8', 'trade_type': 'JSAPI', 'return_code': 'SUCCESS', 'err_code_des': 'SUCCESS', 'mch_id': '1314306201', 'settlement_total_fee': '101', 'cash_fee': '101', 'is_subscribe': 'Y', 'return_msg': 'OK', 'bank_type': 'CMC', 'total_fee': '101', 'appid': 'wxc4aee3cd21013de2', 'result_code': 'SUCCESS', 'err_code': 'SUCCESS'}
@Route(r"/wechatpay/orderNotify")
class _(BaseHandler):
    @coroutine
    def post(self):
        jsonbody = self.xmlToArray(self.request.body)
        logging.info(jsonbody) 
        payment = {}
        if jsonbody.has_key("out_trade_no") and jsonbody.has_key("total_fee"):
            if jsonbody.has_key("sign"):
                requestsign = jsonbody["sign"]
                del jsonbody["sign"]
                global m_id
                global m_key
                logging.info(jsonbody)
                verifiedSign =  self.createSign(jsonbody, m_key)
                logging.info(requestsign)
                logging.info(verifiedSign)
                if requestsign != verifiedSign:
                    xmlresponse = self.arrayToXml({"return_code":"FAIL","return_msg":"SIGNERROR"})
                    logging.info(xmlresponse) 
                    self.write(xmlresponse)
                    self.finish()
                    return

            pay_rec = yield self.fetchone_db("select * from t_payment_record where id=%s",jsonbody["out_trade_no"])
            if str(pay_rec["paid_money"]) != jsonbody["total_fee"]:
                xmlresponse = self.arrayToXml({"return_code":"FAIL","return_msg":"TOTALFREE"})
                logging.info(xmlresponse) 
                self.write(xmlresponse)
                self.finish()
                return

            payment["id"] = jsonbody["out_trade_no"]
            payment["paid_end_time"] = jsonbody["time_end"]
            payment["paid_number"] = jsonbody["total_fee"]
            contact_res = yield self.update_db_by_obj('t_payment_record', payment,"id='%s'" % payment["id"])  

        xmlresponse = self.arrayToXml({"return_code":"SUCCESS","return_msg":"OK"})
        logging.info(xmlresponse) 
        self.write(xmlresponse)
        self.finish()
        

@Route(r"/wechatpay/orderQuery")
class _(BaseHandler):
    @assert_user
    @coroutine
    def post(self):
        args = self.get_args({
            "event_id":"*",
            "id_who":"*"
        })
        pay_rec = yield self.fetchone_db("select * from t_payment_record where event_id=%s and id_who=%s and paid_number='' order by paid_start_time desc",args["event_id"],args["id_who"])
        global m_id
        global m_key
                
        # if use_sandbox:
        #     signkey = yield self.getsignkey(m_id,generate_uunum()[0:32],trade_key)
        #     logging.info(signkey)
        #     m_key = signkey["sandbox_signkey"]
        order = dict(app_id= self.config['wechat_appid'],
                      mch_id= m_id,
                      out_trade_no= pay_rec["id"],
                      nonce_str = generate_uunum()[0:32]
                      )
        logging.info(m_key)
        order["sign"] = self.createSign(order, m_key)
        logging.info(order) 

        wxpay = WXPay(app_id= self.config['wechat_appid'], 
              mch_id= m_id,
              key= m_key, 
              cert_pem_path='',
              key_pem_path='',
              timeout=6000,
              use_sandbox=use_sandbox)  # 毫秒

        jsonbody = wxpay.orderquery(order)
        logging.info(jsonbody)
        payment = {}
        if jsonbody.has_key("out_trade_no") and jsonbody.has_key("total_fee"):
            payment["id"] = jsonbody["out_trade_no"]
            payment["paid_end_time"] = jsonbody["time_end"]
            payment["paid_number"] = jsonbody["total_fee"]
            contact_res = yield self.update_db_by_obj('t_payment_record', payment,"id='%s'" % payment["id"])  
            yield self.restful({"status":"ok"})
        else:
            yield self.restful({"status":"error"})