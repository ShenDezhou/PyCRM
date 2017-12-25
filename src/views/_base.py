# -*- coding: utf-8 -*-  

import tornado.web
import json, datetime, time, decimal
from lib import asynctorndb
import tornado.gen
import sys, random
sys.path.insert(0, "..")
from config import settings
from util.session import Session
from error_code import ERROR_CODE
import redis
import functools
import hashlib
from util.encrypt import assert_encrypt_url
from util import dump_json
from tornado.gen import coroutine, Return
from lib.asynctorndb.converters import escape_item, encoders, decoders, escape_string
from lib.asynctorndb._compat import PY2, range_type, text_type, str_type, JYTHON, IRONPYTHON
import collections
import tornado.escape
from lib import html2text
import torndb
import logging
from lib import wechat_sign


class ConnQueue(object):
    """ Tornado future based deque. """

    def __init__(self, settings = None):
        self.config = settings
        maxlen = self.config['mysql_max_conn']
        self.p_size = maxlen
        self.is_init = False
        self._queue = collections.deque(maxlen=maxlen+10)
        self.waiter = collections.deque()
        self.max_size = maxlen
        
    def get_current_size(self):
        return len(self._queue)

    def get_item(self):
        if len(self._queue) > 0:
            item = self._queue.popleft()
            return item
        else:
            return None

    def put_item(self, item):
        self._queue.append(item)

    @coroutine
    def add_conn(self):
        if self.get_current_size() >= self.max_size:
            return
        conn = asynctorndb.Connect(
            host=self.config['mysql_host'], 
            port=self.config['mysql_port'], 
            user=self.config['mysql_user'], 
            passwd=self.config['mysql_password'], 
            database=self.config['mysql_database'], 
            charset=self.config['mysql_charset'])
        yield conn.connect()
        self.put_item(conn)

    @coroutine
    def init_conn(self):
        self.is_init = True
        for i in xrange(self.p_size):
            yield self.add_conn()

#DB_POOL = {}
#db_pool = ConnQueue(config)

# for d in settings['apps']:
config = settings['apps'][0]
app_settings = {}
db = torndb.Connection(config['mysql_host'], config['mysql_database'], config['mysql_user'], config['mysql_password'])
res = db.query("select * from t_settings")
for r in res:
    app_settings[r['st_id']] = r["st_value"]
db.close()

def genenate_file_key(content = None, filepath = None):
    if filepath:
        content = open(filepath, 'rb').read()
    m = hashlib.md5()
    m.update(content)
    return m.hexdigest()


def assert_user(method):
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if not self.current_user:
            if isinstance(self, BasePage):
                self.redirect("/mgr/login")
            else:
                self.response_error('access_not_allow')
            return
        return method(self, *args, **kwargs)
    return wrapper

def assert_user_or_super(method):
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if not self.current_user and not assert_encrypt_url(self.request.uri) and not self.current_mgr:
            if isinstance(self, BasePage):
                self.redirect("/login")
            else:
                self.response_error('access_not_allow')
            return
        return method(self, *args, **kwargs)
    return wrapper




def assert_manager(method=None, role='', module=''):
    def _assert_manager(method):
        @functools.wraps(method)
        def wrapper(self, *args, **kwargs):
            if not self.current_mgr or self.session.get("mgr-" + str(self.current_mgr) + "-" + module) != module:
                if isinstance(self, MgrPage):
                    self.redirect("/acmlogin")
                else:
                    self.response_error('access_not_allow')
                    raise tornado.web.HTTPError(status_code = 403, log_message="")
                return
            return method(self, *args, **kwargs)
        return wrapper

    if not method:
        def waiting_for_func(method):
            return _assert_manager(method)
        return waiting_for_func
    else:
        return _assert_manager(method)


from lte_util import get_now_str

class BaseHandler(tornado.web.RequestHandler):

    def __init__(self,  *argc, **argkw):
        super(BaseHandler, self).__init__(*argc, **argkw)
        self.session = Session(self.application.session_manager, self)
        # Reuse the redis connection for session manager as a cache store
        self.cache_server = self.application.session_manager.redis
        self.conn = None
        self.conn_slave = None
        self.current_user_profile = None
        self.app_id = self.request.host.split(':')[0].lower()
        # if self.app_id not in DB_POOL:
        self.app_id = app_settings['app_id']
        # logging.info('APP:%s' % self.app_id)
        # if self.app_id and self.app_id in DB_POOL:
        self.db_pool = ConnQueue(settings['apps'][0]) # DB_POOL[self.app_id]
        # else:
        #     self.db_pool = None
        # logging.info(self.db_pool)
        self.config = app_settings

    def is_wechat(self):
        return self.request.headers['User-Agent'].find('MicroMessenger') > 0

    def is_auth(self):
        return self.current_user_profile

    def is_admin(self):
        return self.current_user_profile

    def is_member(self):
        return self.current_user_profile and self.current_user_profile['member']


    #merge peron using cellphone
    @tornado.gen.coroutine
    def merge_person(self,cellphone=None,auth_id=None,email=None,corp_open_id=None):
        if cellphone and auth_id:
            yield self.merge_person_cellphone(cellphone,auth_id)

        if email and auth_id:
            yield self.merge_person_email(email,auth_id)
    
        if cellphone and corp_open_id:
            auth_res = yield self.fetchone_db("select * from t_person where corp_open_id=%s",corp_open_id)
            person = yield self.fetchone_db("select person_id from t_person where cellphone=%s and person_id!=%s",cellphone,auth_res['person_id'])
            if auth_res and person:
                yield self.update_db("""update t_person 
                                        set corp_open_id = %s, user_id = %s, fullname = %s, auth_date = %s,
                                        gender = %s, cellphone = %s, email = %s, wechatid = %s, position = %s, avatar = %s
                                        where person_id=%s""", 
                                    corp_open_id,auth_res['user_id'],auth_res['fullname'], get_now_str(), 
                                    auth_res['gender'], auth_res['cellphone'], auth_res['email'], auth_res['wechatid'], auth_res['position'], auth_res['avatar'], 
                                   person['person_id'])
                yield self.execute_db("""delete from t_person 
                                        where person_id = %s """,auth_res['person_id'])
                
        if email and corp_open_id:
            auth_res = yield self.fetchone_db("select * from t_person where corp_open_id=%s",corp_open_id)
            person = yield self.fetchone_db("select person_id from t_person where email=%s and person_id!=%s",email,auth_res['person_id'])
            if auth_res and person:
                if auth_res['cellphone'] != person['cellphone']:
                    cellphone = auth_res['cellphone']
                    cellphone1 = person['cellphone']
                else:
                    cellphone = auth_res['cellphone']
                    cellphone1 = ''   
                yield self.update_db("""update t_person 
                                            set corp_open_id = %s, user_id = %s, fullname = %s, auth_date = %s,
                                            gender = %s, cellphone = %s, email = %s, wechatid = %s, position = %s, avatar = %s
                                            where person_id=%s""", 
                                        corp_open_id,auth_res['user_id'],auth_res['fullname'], get_now_str(), 
                                        auth_res['gender'], auth_res['cellphone'], auth_res['email'], auth_res['wechatid'], auth_res['position'], auth_res['avatar'], 
                                       person['person_id'])
                yield self.execute_db("""delete from t_person 
                                            where person_id = %s """,auth_res['person_id'])

    @tornado.gen.coroutine
    def merge_person_cellphone(self,cellphone,auth_id):
        if cellphone and auth_id:
            auth_res = yield self.fetchone_db("select * from t_person where auth_id=%s",auth_id)
            person = yield self.fetchone_db("select person_id from t_person where cellphone=%s and person_id<>%s",cellphone,auth_res['person_id'])
            if auth_res and person:
                yield self.update_db("""update t_person 
                                        set auth_id = %s, open_id = %s, web_open_id = %s, auth_date = %s,
                                        nick_name = %s, head_img_url = %s, gender = %s, city = %s, province = %s, country = %s
                                        where person_id=%s""", 
                                    auth_id,auth_res['open_id'],auth_res['web_open_id'], get_now_str(), 
                                    auth_res['nick_name'], auth_res['head_img_url'], auth_res['gender'], auth_res['city'], auth_res['province'], auth_res['country'], 
                                   person['person_id'])
                yield self.execute_db("""delete from t_person 
                                        where person_id = %s """,auth_res['person_id'])

            auth_res = yield self.fetchone_db("select * from t_person where auth_id=%s",auth_id)
            if auth_res and auth_res['email']:
                yield self.merge_person_email(auth_res['email'],auth_id)


    #merge peron using email
    @tornado.gen.coroutine
    def merge_person_email(self,email,auth_id):
        auth_res = yield self.fetchone_db("select * from t_person where auth_id=%s",auth_id)
        person = yield self.fetchone_db("select * from t_person where email=%s and person_id!=%s",email,auth_res['person_id'] )
        if auth_res and person:
            if auth_res['cellphone'] != person['cellphone']:
                cellphone = auth_res['cellphone']
                cellphone1 = person['cellphone']
            else:
                cellphone = auth_res['cellphone']
                cellphone1 = ''
            yield self.update_db("""update t_person 
                                    set auth_id = %s, open_id = %s, web_open_id = %s, auth_date = %s,
                                    nick_name = %s, head_img_url = %s, gender = %s, city = %s, province = %s, country = %s, cellphone = %s, cellphone1 = %s
                                    where person_id= %s""", 
                                auth_id,auth_res['open_id'],auth_res['web_open_id'], get_now_str(), 
                                auth_res['nick_name'], auth_res['head_img_url'], auth_res['gender'], auth_res['city'], auth_res['province'], auth_res['country'],
                                cellphone,cellphone1,
                               person['person_id'])

            yield self.execute_db("""delete from t_person 
                                    where person_id = %s""",auth_res['person_id'])

    @tornado.gen.coroutine
    def refresh_user_profile(self):
        user_id = self.current_user
        handler = self
        if not user_id or handler.get_cache("user-profile-refreshed-%s" % user_id):
            return
        
        profile = {}
        profile['authorized'] = yield handler.fetchone_db("select * from t_person where auth_id=%s", user_id)
        profile['member'] = yield handler.fetchone_db("select t.* , c.code_name as member_type_name from t_member as t left join t_codes as c on c.code_id = t.member_type  where t.auth_id=%s", user_id)
        profile['person'] = yield handler.fetchone_db("select a.* from t_person as a where a.auth_id=%s", user_id)
        profile['org'] = yield handler.fetchone_db("select a.* from t_org as a, t_person as b, t_org_person as c where b.auth_id=%s and c.person_id = b.person_id and c.org_id = a.org_id", user_id)
        profile['roles'] = yield handler.query_db("select a.* from t_auth_role as a where a.auth_id=%s", user_id)

        handler.set_cache("user-profile-" + user_id, dump_json(profile), 86400*300)
        handler.set_secure_cookie("user", user_id, expires_days = 300)
        handler.set_cache("user-profile-refreshed-%s" % user_id, '1', 60)

    def escape(self, obj):
        ''' Escape whatever value you pass to it  '''
        if isinstance(obj, str_type):
            return "'" + escape_string(obj) + "'"
        return escape_item(obj, 'utf-8')

    def escape_string(self, s):
        return tornado.escape.xhtml_escape(escape_string(s))

    def limit_action(self, key, max_times = 200):
        res = self.session.get(key) or 0
        if res and int(res) > max_times:
            return True
        self.session.set(key, int(res) + 1)
        return False

    @tornado.gen.coroutine
    def add_traffic(self, key, t):
        yield self.insert_db("insert into ac_traffic (item_id, item_type, created, ip) values (%s, %s, now(), %s)", key, t, self.request.remote_ip)

    def set_cache_obj(self, key, value, timeout=60):
        self.set_cache(key, dump_json(value), timeout)

    def set_cache(self, key, value, timeout=60):
        if len(key) > 200:
            key = genenate_file_key(key)
        self.cache_server.setex(self.config['app_id'] + '-' + key, timeout, value)

    def get_cache_obj(self, key):
        r = self.get_cache(key)
        if r:
            return json.loads(r)
        return ''

    def get_cache(self, key):
        if len(key) > 200:
            key = genenate_file_key(key)
        return self.cache_server.get(self.config['app_id'] + '-' + key)

    @tornado.gen.coroutine
    def do_task(self, func, queue, args):
        key = 'task-working-' + genenate_file_key(dump_json(args))
        if self.get_cache(key):
            raise tornado.web.gen.Return(None)
            return

        res = None
        try:
            self.set_cache(key, args, 60)
            res = yield tornado.gen.Task(
                    func, 
                    queue = queue, 
                    args=args)
            self.set_cache(key, '', 1)
        except:
            self.set_cache(key, '', 1)
            raise tornado.web.gen.Return(None)
            return

        raise tornado.web.gen.Return(res)

    def check_login(self):
        if not self.current_user:
            self.redirect("/login")
            # self.finish()
            return

    @tornado.gen.coroutine
    def redirect_unauth(self):
        if isinstance(self, BasePage):
            self.close_db_conn()
            self.redirect("/page/unauth")
        else:
            self.close_db_conn()
            yield self.response_error('access_not_allow')

    def get_current_user(self):
        user = self.get_secure_cookie("user")
        return user

    @tornado.gen.coroutine
    def refresh_app_config(self):
        k = self.app_id + '-app-config-refreshed'
        if not self.get_cache(k):
            res = yield self.query_db("select * from t_settings")
            settings = {}
            for r in res:
                settings[r['st_id']] = r["st_value"]
            self.config = settings
            self.set_cache(k, 1, 60)
            logging.info("refresh app config of %s" % self.app_id)

        # 刷新用户profile
        # yield self.refresh_user_profile()

    @tornado.gen.coroutine
    def get_db_conn(self, master = False):
        if self.conn and self.conn.stream and not self.conn.stream.closed():
            raise tornado.web.gen.Return(self.conn)
            return

        if not self.app_id or not self.db_pool:
            yield self.error('网络错误，应用不存在')
            raise tornado.web.gen.Return(None)
            return

        if not self.db_pool.is_init:
            yield self.db_pool.init_conn()
        conn = self.db_pool.get_item()
        if not conn:
            yield self.error('网络繁忙，请稍候重试')
            raise tornado.web.gen.Return(None)
            return
        self.conn = conn
        if self.conn.stream.closed():
            yield self.conn.connect()

        yield self.refresh_app_config()

        raise tornado.web.gen.Return(self.conn)
        

    @tornado.gen.coroutine
    def execute_batch_db(self,  *args, **kwargs):
        conn = yield self.get_db_conn(True)
        try:
            res = yield conn.executebatch(*args, **kwargs)
            raise tornado.gen.Return(res)
        except:
            logging.error("Error to executebatch %s" % str(sys.exc_info()))
            raise tornado.gen.Return(False)
        

    @tornado.gen.coroutine
    def callproc_db(self,  *args, **kwargs):
        conn = yield self.get_db_conn()
        res = yield conn.query(*args, **kwargs)
        ### fix issue
        yield conn.next_result()
        raise tornado.gen.Return(res or [])

    @tornado.gen.coroutine
    def query_db(self,  *args, **kwargs):
        conn = yield self.get_db_conn()
        res = yield conn.query(*args, **kwargs)
        #raise tornado.web.HTTPError(500, log_message="Query Failed")
        raise tornado.gen.Return(res or [])

    @tornado.gen.coroutine
    def fetchone_db(self,  *args, **kwargs):
        args = list(args)
        args[0] = args[0] + ' LIMIT 0,1'
        res = yield self.query_db(*args, **kwargs)
        if res and len(res) > 0:
            raise tornado.gen.Return(res[0])
        raise tornado.gen.Return(None)

    @tornado.gen.coroutine
    def update_db(self, *args, **kwargs):
        conn = yield self.get_db_conn(True)
        res = yield conn.update(*args, **kwargs)
        raise tornado.gen.Return(res)

    @tornado.gen.coroutine
    def insert_db_by_obj(self, table, obj):
        keys = []
        vals = []
        for k in obj:
            keys.append(k)
            vals.append(obj[k])
        sql = '''insert into %s (%s) values (%s)''' % (table, ','.join(keys), ('%s,' * len(keys))[:-1] )
        res = yield self.insert_db(sql, *vals)
        raise tornado.gen.Return(res)

    @tornado.gen.coroutine
    def update_db_by_obj(self, table, obj ,condition):
        keys = []
        vals = []
        sets = []
        for k in obj:
            keys.append(k)
            vals.append(obj[k])
            sets.append(str(k) + '=%s')
        sql = '''update %s set %s''' % (table, ','.join(sets))
        res = yield self.update_db(sql + " where " + condition, *vals)
        raise tornado.gen.Return(res)

    @tornado.gen.coroutine
    def insert_db(self, *args, **kwargs):
        conn = yield self.get_db_conn(True)
        res = yield conn.insert(*args, **kwargs)
        raise tornado.gen.Return(True)

    @tornado.gen.coroutine
    def insert_db_and_return_last_insert_id(self, *args, **kwargs):
        conn = yield self.get_db_conn(True)
        args_list = list(args)
        args_list[0] = "%s; SELECT LAST_INSERT_ID()" % args[0]
        n_args = tuple(args_list)
        res = yield conn.insert(*n_args, **kwargs)
        raise tornado.gen.Return(True)

    @tornado.gen.coroutine
    def execute_db(self, *args, **kwargs):
        conn = yield self.get_db_conn(True)
        res = yield conn.execute(*args, **kwargs)
        raise tornado.gen.Return(res)

    @tornado.gen.coroutine
    def execute_rowcount_db(self, *args, **kwargs):
        conn = yield self.get_db_conn()
        res = yield conn.execute_rowcount(*args, **kwargs)
        raise tornado.gen.Return(res)

    def get_safe_text_argument(self, key, default = None):
        return self.get_escaped_argument(key)

    def get_escaped_argument(self, key, default = None):
        arg = self.get_argument(key, default)
            
        if type(arg) == type(''):
            arg = self.escape_string(arg)
        
        return arg

    def get_args(self, keys):
        res = {}
        if type(keys) == type([]):
            for k in keys:
                res[k] = self.get_escaped_argument(k)
        else:
            for k in keys:
                res[k] = self.get_escaped_argument(k) if keys[k] == '*' else self.get_escaped_argument(k, keys[k])
                if keys[k] == '*' and not res[k]:
                    return None
        return res


    @tornado.gen.coroutine
    def response_as_json(self, res):
        self.set_header("Content-Type", 'text/html; charset="utf-8"')
        self.write(dump_json(res))
        self.finish()
        
    @tornado.gen.coroutine
    def restful(self, res):
        yield self.response_as_json(res)

    @tornado.gen.coroutine
    def success(self, txt):
        yield self.restful({'message': txt})

    @tornado.gen.coroutine
    def response_error(self, error_name, status_code=0):
        """
        write error message
        :param error_name:
        :param status_code
        """
        if status_code == 0:
            self.set_header("Content-Type", 'text/html; charset="utf-8"')
            e = ERROR_CODE[error_name] if error_name in ERROR_CODE else {'error': error_name, 'error_code': '911'}
            res = {
                'error': e['error'],
                'error_code': e['error_code'],
                'error_name': error_name   
            }
            self.write(json.dumps(res))
            #self.finish()
            raise tornado.web.Finish()
            if settings['debug']:
                logging.info('response_error%s'%res)
        else:
            raise tornado.web.HTTPError(status_code=status_code, log_message=error_name)
            if settings['debug']:
                logging.info('response_error', status_code, error_name)

    @tornado.gen.coroutine
    def error(self, error_name, status_code=0):
        yield self.response_error(error_name, status_code)

    # @tornado.gen.coroutine
    def close_db_conn(self):
        #释放master
        if self.db_pool and self.conn:
            self.db_pool.put_item(self.conn)


    @tornado.gen.coroutine
    def get_current_user_by_order(self, order_id):
        if order_id:
            order = yield self.fetchone_db("select user_id from order_info where order_id = %s", order_id)
            if order:
                user_id = order.user_id
                raise tornado.gen.Return(user_id)
        raise tornado.gen.Return('')

    @property
    def current_user(self):
        """
        get current adminstrator
        :return: manager_code 
        """
        return self.get_current_user()

    @property
    def current_mgr(self):
        """
        get current adminstrator
        :return: manager_code 
        """
        return self.get_secure_cookie("mgr")

    def on_finish(self):
        self.close_db_conn()


    def error_process(self,message):
        response = json.loads(message)
        error_code = response.get('errcode')
        if error_code and error_code == 40001:
            wechat_sign.Sign(self.config['wechat_appid'], self.config['wechat_secret'],  self.config['site_host_url'],self).clearCache()
        return error_code
    
    def get_person_args(self):
        person_args = self.get_args({
            'fullname': '',
            'gender': '',
            'birthday':'',
            'school':'',
            'school_start':'',
            'education':'',
            'wechatid':'',
            'cellphone':'*',
            'cellphone1':'',
            'cellphone2':'',
            'email': '',
            'email1': '',
            'email2': '',
            'address': '',
            'school_number':'',
            'school_department':'',
            'person_info':'',
            'expects': '',
            'wills': ''
        })
        return person_args

    @coroutine
    def member_type_list(self,advanced=False,normal=False,org=False,person=False,code_name=False):
        '''
        返回所有按照条件查询的会员类型,可选择返回code_id或者code_name,默认返回code_id
        :param advanced: 理事会员
        :param normal: 普通会员
        :param org: 企业会员
        :param person: 个人会员
        :param code_name: 会员中文名称
        :return:
        '''
        member_types = list()
        if advanced:
            member_types = yield self.query_db(
                "select code_id,code_name from t_codes where code_id like '%%advanced%%' and code_type = 'member_type'")
        elif normal:
            member_types = yield self.query_db(
                "select code_id,code_name from t_codes where code_id not like '%%advanced%%' and code_type = 'member_type'")
        elif org:
            member_types = yield self.query_db(
                "select code_id,code_name from t_codes where code_id like '%%org%%' and code_type = 'member_type'")
        elif person:
            member_types = yield self.query_db(
                "select code_id,code_name from t_codes where code_id not like '%%org%%' and code_type = 'member_type'")
        else:
            member_types = yield self.query_db(
                "select code_id,code_name from t_codes where code_type = 'member_type'")
        if code_name:
            raise tornado.gen.Return([i.code_name for i in member_types])
        else:
            raise tornado.gen.Return([i.code_id for i in member_types])



class MgrHandler(BaseHandler):

    @tornado.gen.coroutine
    def log_op(self, op_type, op_id, op_content):
        '''
        这段代码没被使用，记录后台操作日志
        :param op_type:
        :param op_id:
        :param op_content:
        :return:
        '''
        mgr_id = self.current_mgr
        yield self.insert_db("insert into ac_mgr_log (mgr_id, op_type, op_id, op_content, created) values (%s, %s, %s, %s, now()) ",
                            mgr_id,
                            op_type,
                            op_id,
                            dump_json(op_content) if type(op_content) != type('') else op_content,
                            )
    

class BasePage(BaseHandler):
    def prepare(self):
        self.xsrf_token

class MgrPage(MgrHandler):
    def prepare(self):
        self.xsrf_token


