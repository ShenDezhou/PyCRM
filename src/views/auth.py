# -*- coding: utf-8 -*-  

from util import dump_json
import redis
import functools
from tornado.gen import coroutine, Return
import json, os
from util import dump_json
from _base import * 
from lte_util import * 
from util.encrypt import encrypt_pwd
from config import settings


ROLES = json.loads(open(os.path.join(os.path.dirname(__file__), "constants/roles.json"), "rb").read())

NAVS = json.loads(open(os.path.join(os.path.dirname(__file__), "constants/mgr_navs.json"), "rb").read())

def get_role_name(role_id):
    for r in ROLES:
        if role_id == r['id']:
            return r["name"]
    return ""

@coroutine
def get_mgr_navs(handler):
    profile = handler.current_user_profile
    navs = []
    if profile and 'roles' in profile and not is_role_in(profile['roles'], ['admin']):
        role_pages = yield handler.query_db("select distinct page_id from t_role_page where role_id in ('%s')" % "','".join([r['role_id'] for r in profile['roles']]))
        role_pages = [r['page_id'] for r in role_pages] 
        for n in NAVS:
            if ('child' in n and is_list_in(n['child'],role_pages)) or n['id'] in role_pages or n['id'].startswith('mgr_settings'):
                navs.append(n)
    else:
        for n in NAVS:
            navs.append(n)
    raise Return(navs)

def is_list_in(roles1, roles2):
    for r1 in roles1:
        if r1 in roles2:
            return True
    return False

def is_role_in(roles1, roles2):
    for r1 in roles1:
        if r1['role_id'] in roles2:
            return True
    return False

def is_member_in(member, members):
    for m in member:
        if m['member_type'] in members:
            return True
    return False

def check_auth(handler, roles = None, members = None, is_member = False):
    profile = handler.current_user_profile
    if not profile:
        return False
    if roles and ('roles' not in profile or not is_role_in(profile['roles'], roles)):
        return False
    if (is_member is True or members) and ('member' not in profile or not profile['member']):
        return False
    if type(members) == type([]) and ('member' not in profile or not is_member_in(profile['member'], members)):
        return False
    return True

def preassert_user(method=None, roles='', modules=''):

    def _assert_usr(method):
        @functools.wraps(method)
        def wrapper(self, *args, **kwargs):

            if self.current_user:            
                profile_cache = self.get_cache("user-profile-" + self.current_user)

                if profile_cache:
                    self.current_user_profile = json.loads(profile_cache)

            return method(self, *args, **kwargs)
        return wrapper

    if not method:
        def waiting_for_func(method):
            return _assert_usr(method)
        return waiting_for_func
    else:
        return _assert_usr(method)


def assert_user(method):
    def go_out(handler):
        if isinstance(handler, BasePage):
            handler.set_secure_cookie('redirect_url', handler.request.uri)
            handler.redirect("/login")
        else:
            handler.response_error('access_not_allow')
        return

    @functools.wraps(method)
    @coroutine
    def wrapper(self, *args, **kwargs):

        if not self.current_user:
            go_out(self)
            return 

        profile_cache = self.get_cache("user-profile-" + self.current_user)
        user_section  = self.session.get("user-section")
        user_cookie   = self.get_secure_cookie("user")

        if not user_section:
            if user_cookie:
                yield login_user(self, person_id = user_cookie)
                profile_cache = self.get_cache("user-profile-" + user_cookie)
            elif not profile_cache:
                go_out(self)
                return
        
        self.current_user_profile = json.loads(profile_cache)
        profile = self.current_user_profile
        if self.request.uri.startswith('/console/') and not is_role_in(profile['roles'], ['admin']):
            if 'roles' in self.current_user_profile and self.current_user_profile['roles']:
                entry = 'mgr_' + self.request.uri.split('/')[-1].split('?')[0].split('#')[0][:30]
                if not entry.startswith('mgr_settings') and entry != 'mgr_unauth':
                    page = get_mgr_page_by_entry(entry)
                    if page['id'] == entry:
                        res = yield self.fetchone_db("select page_id from t_role_page where page_id = '%s' and role_id in ('%s')" % (entry, "','".join([r['role_id'] for r in profile['roles']])) )
                        if not res:
                            self.redirect("/console/unauth")
                            return

        res = yield method(self, *args, **kwargs)

        raise Return(res)

    return wrapper

@coroutine
def login_user(handler, union_id=None,corp_open_id=None,person_id=None,open_id=None):
    profile = {}
    if union_id:
        profile['authorized'] = yield handler.fetchone_db("select * from t_person where auth_id=%s", union_id)

    if corp_open_id:
        profile['authorized'] = yield handler.fetchone_db("select * from t_person where corp_open_id=%s", corp_open_id)
        logging.info('corp_open_id :%s' % corp_open_id)

    if person_id:
        profile['authorized'] = yield handler.fetchone_db("select * from t_person where person_id=%s", person_id)

    if open_id:
        profile['authorized'] = yield handler.fetchone_db("select * from t_person where open_id=%s", open_id)

    if profile['authorized']:
        person_id = profile['authorized']['person_id']
        logging.info("login_user:%s"%person_id)
        profile['member'] = yield handler.query_db("""(select t.* , c.code_name as member_type_name
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
        profile['person'] = yield handler.fetchone_db("select a.* from t_person as a where a.person_id=%s", person_id)
        profile['org'] = yield handler.fetchone_db("select a.* from t_org as a, t_person as b, t_org_person as c where b.person_id=%s and c.person_id = b.person_id and c.org_id = a.org_id order by c.updated DESC", person_id)
        profile['roles'] = yield handler.query_db("select a.*, b.code_name as role_name from t_auth_role as a, t_codes as b where a.person_id=%s and b.code_id = a.role_id and b.code_type = 'mgr_role'", person_id)

        handler.set_cache("user-profile-" + person_id, dump_json(profile), 86400*300)
        handler.set_secure_cookie("user", person_id, expires_days = 300)
        handler.session.set("user-section", person_id)

        handler.current_user_profile = profile
        raise Return((True, "登录成功"))
    else:
        logout_user(handler)
        raise Return((False, "登录失败"))
        
@coroutine
def logout_user(handler):
    if handler.current_user:
        handler.session.set("user-section", '')
        handler.set_cache("user-profile-" + handler.current_user, '')
    handler.clear_cookie('user')
    raise Return((True, "成功退出登录"))

def assert_mgr(method):
    def go_out(handler):
        if isinstance(handler, BasePage):
            #
            handler.set_secure_cookie('redirect_url', handler.request.uri)
            handler.redirect("/common")
        else:
            handler.response_error('access_not_allow')
            
    def _assert_mgr(method):
        @functools.wraps(method)
        @coroutine
        def wrapper(self, *args, **kwargs):
            if self.current_user:
                auth_role = yield self.fetchone_db("select * from t_auth_role where person_id=%s", self.current_user)
                if not auth_role:
                    go_out(self)
                    return
            else:
                self.redirect("/login")
                return
            profile_cache = self.get_cache("user-profile-" + self.current_user)
            user_section = self.session.get("user-section")
            user_cookie = self.get_secure_cookie("user")

            if not user_section:
                if user_cookie:
                    yield login_user(self, person_id=user_cookie)
                    profile_cache = self.get_cache("user-profile-" + user_cookie)
                elif not profile_cache:
                    go_out(self)
                    return

            self.current_user_profile = json.loads(profile_cache)
            # profile = self.current_user_profile
            # session_value = self.session.get("mgrlogin")
            # if not self.current_mgr:
            #     if isinstance(self, MgrPage):
            #         #self.session.set("mgrlogin", '')
            #         #if self.current_mgr:
            #         #self.set_cache("mgrlogin-" + self.current_mgr, "", 1)
            #         self.redirect("/mgr/login")
            #     else:
            #         self.response_error('access_not_allow')
            #     return
            # self.current_mgr_cache = json.loads(self.get_cache("mgrlogin-" + self.current_mgr))
            # self.session.set("mgrlogin", session_value)

            # check if change password on init
            # if isinstance(self, MgrPage) and self.request.uri.find('/mgr/init_pwd') < 0 and ('pwd_changed' not in self.current_mgr_cache or not self.current_mgr_cache['pwd_changed']):
            #    self.redirect("/mgr/init_pwd")
            #    return
            res = yield method(self, *args, **kwargs)
            raise Return(res)
        return wrapper

    if not method:
        def waiting_for_func(method):
            return _assert_mgr(method)
        return waiting_for_func
    else:
        return _assert_mgr(method)





