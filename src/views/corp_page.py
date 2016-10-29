# -*- coding: utf-8 -*-  
from lib.tornadotools.route import Route
from _base import BasePage,BaseHandler ,MgrPage,MgrHandler
from config import settings
import tornado.gen
import time, hashlib
from tornado.gen import coroutine, Return, Task
from tornado.web import asynchronous
from util.validation import is_valid_email, is_valid_phone, is_valid_password, is_valid_name ,is_valid_number
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
from wechat_sdk import WechatBasic
from util.send_phone_email import send_email

from wechatpy.enterprise.crypto import WeChatCrypto
from wechatpy.exceptions import InvalidSignatureException
from wechatpy.enterprise.exceptions import InvalidCorpIdException
from wechatpy.enterprise import parse_message, create_reply, WeChatClient

#企业号回调
#微信登录成功
@Route(r"/wechatcorplogin")
class _(BasePage):
    @coroutine
    def get(self):
        code = self.get_argument('code', '')
        if not code:
            logging.info('error wechat login')
            return

        client = WeChatClient(self.config['wechat_corpid'], self.config['wechat_corp_secret'])
        logging.info("code:%s" % code)
        body = client.user.get_info(1,code)
        logging.info("%s" % body)
        
        if body.get('UserId'):
            body = client.user.get(body.get('UserId'))
            logging.info("%s" % body)
            
            corp_open_id_body = client.user.convert_to_openid(body.get('userid'),0)
            logging.info("%s" % corp_open_id_body)

            res_person = yield self.fetchone_db("""select * from t_person where cellphone=%s""", body['mobile'])
            if not res_person:
                uuid = corp_open_id_body.get('openid')
                args = {
                'person_id':  generate_uuid(),
                'corp_open_id':corp_open_id_body.get('openid'),
                'user_id': body.get('userid'),
                'fullname': body.get('name'),
                'gender': body.get('gender'),
                'cellphone':body.get('mobile'),
                'email': body.get('email'),
                'wechatid':body.get('weixinid'),
                'position':body.get('position'),
                'type':'weixin_corp',
                'weixin_created': get_now_str(),
                'auth_date': get_now_str(),
                'head_img_url':body.get('avatar'),
                'avatar':body.get('avatar')
                }
                
                # 尚未授权过，将用户信息插入授权用户表,用户表
                yield self.insert_db_by_obj('t_person', args)
            else:
                uuid = res_person['corp_open_id']
                args = {
                'corp_open_id':corp_open_id_body.get('openid'),
                'user_id': body.get('userid'),
                'fullname': body.get('name'),
                'gender': body.get('gender'),
                'cellphone':body.get('mobile'),
                'email': body.get('email'),
                'wechatid':body.get('weixinid'),
                'position':body.get('position'),
                'type':'weixin_corp',
                'weixin_created': get_now_str(),
                'auth_date': get_now_str(),
                'head_img_url':body.get('avatar'),
                'avatar':body.get('avatar')
                }
                for key in args.keys():
                    if args[key]=='':
                        args.pop(key)

                yield self.update_db_by_obj('t_person', args,"cellphone='%s'" % body['mobile'])
        elif body.get('OpenId'):
            uuid = body.get('OpenId')
            res_person = yield self.fetchone_db("""select * from t_person where corp_open_id=%s""", uuid)
            if not res_person:
                # body = client.user.create(uuid, uuid)
                # logging.info("create user_corp: %s" % body)

                args = {
                'person_id': generate_uuid(),
                'corp_open_id':uuid,
                'type':'weixin_corp',
                'weixin_created': get_now_str(),
                'auth_date': get_now_str()
                }

                # 尚未授权过，将企业用户信息插入用户表
                yield self.insert_db_by_obj('t_person', args)
            
        yield auth.login_user(self, corp_open_id=uuid)

        redirect_url = self.get_secure_cookie('redirect_url') or '/common' # 
        self.set_secure_cookie('redirect_url', '', 1)

        
        self.redirect(redirect_url)



    @coroutine
    def to_remove_get(self):
        code = self.get_argument('code', '')
        if not code:
            logging.info('error wechat login')
            return

        logging.info("wechatcorplogin")
        # 获取accesstoken与openid
        client = tornado.httpclient.AsyncHTTPClient()
        # https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid=id&corpsecret=secrect
        request = tornado.httpclient.HTTPRequest(
                url="https://qyapi.weixin.qq.com/cgi-bin/gettoken?" +
                    urllib.urlencode({"corpid": self.config['wechat_corpid'], "corpsecret": self.config['wechat_corp_secret']
                                      }),
                method="GET",
                validate_cert=False
        )
        resp = yield client.fetch(request)
        body = json.loads(resp.body)
        # openid = body['openid']
        # unionid = body['unionid']
        #refreshtoken=body['refresh_token']
        accesstoken=body['access_token']

        # 获取用户信息
        # https://qyapi.weixin.qq.com/cgi-bin/user/getuserinfo?access_token=ACCESS_TOKEN&code=CODE&agentid=AGENTID
        request = tornado.httpclient.HTTPRequest(
                url="https://qyapi.weixin.qq.com/cgi-bin/user/getuserinfo?"+
                urllib.urlencode({"access_token": accesstoken,  "code": code,
                                  "agentid": "0"}),
                method="GET",
                validate_cert=False
        )
        resp = yield client.fetch(request)
        body = json.loads(resp.body)
        logging.info("%s" % body)


        request = tornado.httpclient.HTTPRequest(
                url="https://qyapi.weixin.qq.com/cgi-bin/user/get?"+
                urllib.urlencode({"access_token": accesstoken,  "userid": body['UserId']}),
                method="GET",
                validate_cert=False
        )
        resp = yield client.fetch(request)
        body = json.loads(resp.body)
        logging.info("%s" % body)
        self.write(body)

        # 是否已经授权过
        

        
        # res = yield self.fetchone_db("""select * from t_authorized_user where cellphone=%s""", body['mobile'])
        # if not res:
        res_person = yield self.fetchone_db("""select * from t_person where cellphone=%s""", body['mobile'])
        if not res_person:
            uuid = generate_uuid()
            args = {
            'person_id': uuid,
            'auth_id':uuid,
            'user_id': body.get('userid'),
            'fullname': body.get('name'),
            'gender': body.get('gender'),
            'cellphone':body.get('mobile'),
            'email': body.get('email'),
            'wechatid':body.get('weixinid'),
            'position':body.get('position'),
            'type':'weixin',
            'weixin_created': get_now_str(),
            'auth_date': get_now_str(),
            'head_img_url':body.get('avatar'),
            'avatar':body.get('avatar')
            }

            # 尚未授权过，将用户信息插入授权用户表,用户表
            yield self.insert_db_by_obj('t_person', args)
        else:
            uuid = res_person['auth_id']
            args = {
            'user_id': body.get('userid'),
            'fullname': body.get('name'),
            'gender': body.get('gender'),
            'cellphone':body.get('mobile'),
            'email': body.get('email'),
            'wechatid':body.get('weixinid'),
            'position':body.get('position'),
            'type':'weixin',
            'weixin_created': get_now_str(),
            'auth_date': get_now_str(),
            'head_img_url':body.get('avatar'),
            'avatar':body.get('avatar')
            }
            for key in args.keys():
                if args[key]=='':
                    args.pop(key)

            yield self.update_db_by_obj('t_person', args,"cellphone='%s'" % body['mobile'])
            

        yield auth.login_user(self, uuid)

        redirect_url = self.get_secure_cookie('redirect_url') or '/common' # 
        self.set_secure_cookie('redirect_url', '', 1)

        
        self.redirect(redirect_url)


#{"key_code":"","person_id":""}
@Route(r"/qr_corplogin")
class _(BasePage):
    @coroutine
    def get(self):
        logging.info(self.get_cache("key_code"))
        str_key_code = self.get_cache("key_code")
        if str_key_code:
            cache_code = json.loads(str_key_code)
            
        else:
            key_code = generate_uuid()
            cache_code = {"key_code":key_code,"person_id":""}
            self.set_cache("key_code", dump_json(cache_code), 60)
        
        ctx = {}  
        ctx['url_for_qr'] = "/rest/qrcode?link=/verify_corplogin?key_code=%s" % cache_code['key_code']
        entry = 'corplogin'
        page = get_page_by_entry(entry)
        
        self.render(page['layout'], 
                    entry = entry,
                    page = page,
                    page_config = map_config,
                    context = ctx) 


#
@Route(r"/verify_corplogin")
class _(BasePage):
    @coroutine
    def get(self):
        logging.info(self.get_cache("key_code"))
        if not self.current_user:
            redirect_url = self.get_secure_cookie('redirect_url') or '/login' # 
            self.redirect(redirect_url)
            return

        scanned_code = self.get_argument('key_code', '')
        str_key_code = self.get_cache("key_code")
        if str_key_code:
            cache_code = json.loads(str_key_code)
            print self.current_user
            print scanned_code,cache_code
            if not scanned_code:
                yield self.error("参数缺失")
                return
            

            if scanned_code and cache_code and scanned_code==cache_code["key_code"]:
                login_pair = {"key_code":scanned_code,"person_id":self.current_user}
                self.set_cache("key_code", dump_json(login_pair), 60)

                redirect_url = self.get_secure_cookie('redirect_url') or '/common' # 
                self.redirect(redirect_url)
        else:
            self.redirect_unauth()


#微信会话
@Route(r"/wechatcorpchat")
class _(BaseHandler):
    @coroutine
    def get(self):

        chatid = self.get_argument('chatid', '')
        client = WeChatClient(self.config['wechat_corpid'], self.config['wechat_corp_im_secret'])
        
        sender = self.get_argument('sender', '')
        receiver_type = self.get_argument('receiver_type', '')
        user_id = self.get_argument('user_id', '')
        content = self.get_argument('content', '')
        if sender:
            if receiver_type == 'single':
                body = client.chat.send_text(chatid,receiver_type,user_id,content)
            if receiver_type == 'group':
                body = client.chat.send_text(chatid,receiver_type,chatid,content)
            logging.info("%s" % body)
            yield self.response_as_json(body)
            return
            
        if chatid:
            body = client.chat.get(chatid)
            logging.info("%s" % body)
            yield self.response_as_json(body)
            return

        