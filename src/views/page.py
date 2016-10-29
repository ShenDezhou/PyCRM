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


@coroutine
def track_visit(self, person_id, visit_target):
    res = yield self.fetchone_db("select visit_count from t_visit where person_id=%s and visit_target=%s", person_id,
                                 visit_target)
    if not res:
        yield self.insert_db_by_obj('t_visit', {
            'visit_target': visit_target,
            'person_id': person_id,
            'first_visited': get_now_str(),
            'last_visited': get_now_str(),
            'visit_count': 1
        })
    else:
        yield self.update_db_by_obj('t_visit', {
            'last_visited': get_now_str(),
            'visit_count': res['visit_count'] + 1
        }, 'person_id=%s and visit_target=%s' % (self.escape(person_id), self.escape(visit_target)))


@Route(r"/")
@Route(r"/home")
@Route(r"/feedback")
class _(BasePage):
    def get(self):
        self.redirect('/page/comingsoon')

#微信服务号回调
@Route(r"/MP_verify_y947glvSRFN8krXb.txt")
class _(BasePage):
    def get(self):
        self.write('y947glvSRFN8krXb')

class CommonPage(BasePage):
    @coroutine
    def get_context(self):
        raise Return({})

    @assert_user
    @coroutine
    def get(self, entry='usercenter'):
        if entry == 'memberinfo' and not self.is_member():
            self.redirect('/page/joinmember')
            return

        ctx = yield self.get_context()
        page = get_common_page_by_entry('common_' + entry)

        self.render(page['layout'],
                    entry=entry,
                    page=page,
                    page_config=map_config,
                    context=ctx)


# START COMMON PAGES
@Route(r"/common")
@Route(r"/common/")
class _(CommonPage):
    # @assert_user
    @coroutine
    def get(self):
        self.redirect('/common/events')


@Route(r"/page/email")
class _(CommonPage):
    @coroutine
    def get(self):
        self.render("test_email_newsletter.html")


@Route(r"/common/(memberinfo)")
class _(CommonPage):
    @coroutine
    def get_context(self):
        ctx = {}
        ctx = self.current_user_profile
        person_id = ctx['person']['person_id']
        res = yield self.fetchone_db(
            "select t.* , code_name from t_form as t left join t_codes as m on m.code_id = t.form_status ,t_form_relation as fr , t_person as p where p.person_id=%s and fr.person_id=p.person_id and fr.form_id=t.form_id and t.form_status != 'paid'",
            person_id)
        ctx['apply_form'] = res
        raise Return(ctx)


@Route(r"/common/(usercenter)")
class _(CommonPage):
    @preassert_user
    @coroutine
    def get_context(self):
        ctx = {}
        ctx['user_profile'] = self.current_user_profile
        raise Return(ctx)


@Route(r"/common/(articles)")
class _(CommonPage):
    @coroutine
    def get_context(self):
        start_id = self.get_argument('start_id', '')
        ctx = {}
        ctx['user_profile'] = self.current_user_profile
        if start_id:
            ctx['articles'] = yield self.query_db(
                "select * from t_article where status = 'published' and id < %s order by id DESC limit 0, 10", start_id)
        else:
            ctx['articles'] = yield self.query_db(
                "select * from t_article where status = 'published' order by id DESC limit 0, 10")
        raise Return(ctx)


@Route(r"/rest/common/articles")
class _(CommonPage):
    @coroutine
    def get(self):
        start_id = self.get_argument('start_id', '')
        ctx = {}
        if start_id:
            ctx['articles'] = yield self.query_db(
                "select a.* from t_article as a, t_article as b where a.status = 'published' and b.id = %s and a.id <> b.id and a.published < b.published order by a.published DESC limit 0, 10",
                start_id)
        else:
            ctx['articles'] = yield self.query_db(
                "select * from t_article where status = 'published' order by published DESC limit 0, 10")
        yield self.restful(ctx)


@Route(r"/common/(events|events_history)")
class _(CommonPage):
    @coroutine
    def get_context(self):
        start_id = self.get_argument('start_id', '')
        ctx = {}
        ctx['user_profile'] = self.current_user_profile
        raise Return(ctx)


@Route(r"/common/(discussion)")
class _(CommonPage):
    @coroutine
    def get_context(self):
        ctx = {}
        ctx['user_profile'] = self.current_user_profile
        raise Return(ctx)

@Route(r"/common/(discussion_new)")
class _(CommonPage):
    @coroutine
    def get_context(self):
        ctx = {}
        ctx['user_profile'] = self.current_user_profile
        id = self.get_argument('id','')
        if id:
            sql = """
                select title,subject,left(published,10) as published, content ,
                        data_type, pictures ,activity_start_time,
                        activity_end_time,activity_type,activity_online_offline,
                        sign_up_check,signup_content,sign_up_fields
                        from t_discussion as a where id = %s and person_id = %s
                """
            result = yield self.query_db(sql, id, self.current_user)
            if not result and not is_role_in(self.current_user_profile['roles'], ['admin']):
                yield self.redirect_unauth()

        raise Return(ctx)
        

@Route(r"/rest/common/events")
class _(CommonPage):
    @coroutine
    def get(self):
        current_user = self.get_current_user()
        start_id = self.get_argument('start_id', '')
        ctx = {}
        if start_id:
            ctx['events'] = yield self.query_db("""
                        select a.id, left(a.published,10) as published,a.title,a.pictures,a.data_source,
                                        a.activity_start_time, a.activity_end_time,
                                        a.activity_sponsor,a.activity_undertake,a.activity_place,a.general_place,
                                        DATE_FORMAT(a.activity_start_time, '%%Y年%%m月%%d日') as activity_start_date,
                                        DATE_FORMAT(a.activity_end_time, '%%Y年%%m月%%d日') as activity_end_date,
                                        DATE_FORMAT(a.activity_start_time, '%%H:%%i') as activity_start_hm,
                                        DATE_FORMAT(a.activity_end_time, '%%H:%%i') as activity_end_hm,
                                        m.code_name as status,
                                        case 
                                            when a.activity_end_time < now() then '活动已结束' 
                                            else '' 
                                        end as event_time_status,
                                        case 
                                            when a.sign_up_limit = 1 then '截止报名'
                                            when t.status = 'sign_up_success' then '报名成功'
                                            when t.status = 'sign_up_wait' then '正在审核'
                                            when t.status = 'sign_up_full' then '人数已满'
                                            when t.status = 'sign_up_fail' then '报名未成功'
                                            else '正常报名' 
                                        end as sign_up_status,
                                        t.status,t.reason
                        from t_news as a left join t_codes as m on a.status = m.code_id
                        left join (select * from t_traffic where person_id = %s) as t on a.id = t.activity_id,
                        (select * from t_news where id = %s ) as b
                        where a.type='activity' and a.status = 'published' and a.activity_start_time >= now() and a.id <> b.id and a.activity_start_time <= b.activity_start_time order by a.activity_start_time DESC limit 0, 10""",
                                                current_user, start_id)
        else:
            ctx['events'] = yield self.query_db("""
                        select a.id, left(published,10) as published,title,pictures,data_source,
                                        activity_start_time, activity_end_time,
                                        activity_sponsor,activity_undertake,activity_place,general_place,
                                        DATE_FORMAT(activity_start_time, '%%Y年%%m月%%d日') as activity_start_date,
                                        DATE_FORMAT(activity_end_time, '%%Y年%%m月%%d日') as activity_end_date,
                                        DATE_FORMAT(activity_start_time, '%%H:%%i') as activity_start_hm,
                                        DATE_FORMAT(activity_end_time, '%%H:%%i') as activity_end_hm,
                                        m.code_name as status,
                                        case 
                                            when a.activity_end_time < now() then '活动已结束' 
                                            else '' 
                                        end as event_time_status,
                                        case 
                                            when a.sign_up_limit = 1 then '截止报名'
                                            when t.status = 'sign_up_success' then '报名成功'
                                            when t.status = 'sign_up_wait' then '正在审核'
                                            when t.status = 'sign_up_full' then '人数已满'
                                            when t.status = 'sign_up_fail' then '报名未成功'
                                            else '正常报名' 
                                        end as sign_up_status,
                                        t.status,t.reason
                        from t_news as a left join t_codes as m on a.status = m.code_id
                        left join (select * from t_traffic where person_id = %s) as t on a.id = t.activity_id
                        where type='activity' and a.status = 'published' and activity_start_time >= now() order by activity_start_time DESC limit 0, 10""",
                                                current_user)
        yield self.restful(ctx)


@Route(r"/rest/common/events_history")
class _(CommonPage):
    @coroutine
    def get(self):
        start_id = self.get_argument('start_id', '')
        ctx = {}
        if start_id:
            ctx['events'] = yield self.query_db("""
                        select a.id, left(a.published,10) as published,a.title,a.pictures,a.data_source,
                                        a.activity_start_time, a.activity_end_time,
                                        a.activity_sponsor,a.activity_undertake,a.activity_place,a.general_place,
                                        DATE_FORMAT(a.activity_start_time, '%%Y年%%m月%%d日') as activity_start_date,
                                        DATE_FORMAT(a.activity_end_time, '%%Y年%%m月%%d日') as activity_end_date,
                                        DATE_FORMAT(a.activity_start_time, '%%H:%%i') as activity_start_hm,
                                        DATE_FORMAT(a.activity_end_time, '%%H:%%i') as activity_end_hm,
                                        m.code_name as status,
                                        case 
                                            when a.activity_end_time < now() then '活动已结束' 
                                            else '' 
                                        end as event_time_status,
                                        case 
                                            when a.sign_up_limit = 1 then '截止报名' 
                                            else '正常报名' 
                                        end as sign_up_status
                        from t_news as a left join t_codes as m on a.status = m.code_id, 
                             t_news as b
                        where a.type='activity' and a.status = 'published' and a.activity_start_time < now() and b.id = %s and a.id <> b.id and a.activity_start_time <= b.activity_start_time order by a.activity_start_time DESC limit 0, 10""",
                                                start_id)
        else:
            ctx['events'] = yield self.query_db("""
                        select id, left(published,10) as published,title,pictures,data_source,
                                        activity_start_time, activity_end_time,
                                        activity_sponsor,activity_undertake,activity_place,general_place,
                                        DATE_FORMAT(activity_start_time, '%%Y年%%m月%%d日') as activity_start_date,
                                        DATE_FORMAT(activity_end_time, '%%Y年%%m月%%d日') as activity_end_date,
                                        DATE_FORMAT(activity_start_time, '%%H:%%i') as activity_start_hm,
                                        DATE_FORMAT(activity_end_time, '%%H:%%i') as activity_end_hm,
                                        m.code_name as status,
                                        case 
                                            when a.activity_end_time < now() then '活动已结束' 
                                            else '' 
                                        end as event_time_status,
                                        case 
                                            when a.sign_up_limit = 1 then '截止报名' 
                                            else '正常报名' 
                                        end as sign_up_status
                        from t_news as a left join t_codes as m on a.status = m.code_id
                        where type='activity' and status = 'published' and activity_start_time < now() order by activity_start_time DESC limit 0, 10""")
        yield self.restful(ctx)


@Route(r"/rest/common/discussion")
class _(CommonPage):
    @coroutine
    def get(self):
        current_user = self.get_current_user()
        to_skip = self.get_argument('to_skip', '')
        if not to_skip:
            to_skip = 0
        target = self.get_argument('target', '')
        ctx = {}
        ctx['discussion'] = yield self.query_db("""
            select a.id, left(published,10) as published,title,pictures,
                            activity_start_time, activity_end_time,
                            DATE_FORMAT(activity_start_time, '%%Y年%%m月%%d日') as activity_start_date,
                            DATE_FORMAT(activity_end_time, '%%Y年%%m月%%d日') as activity_end_date,
                            DATE_FORMAT(activity_start_time, '%%H:%%i') as activity_start_hm,
                            DATE_FORMAT(activity_end_time, '%%H:%%i') as activity_end_hm,
                            m.code_name as status,content,subject,
                            case 
                                when a.activity_end_time < now() then '活动已结束' 
                                else '' 
                            end as event_time_status,
                            case 
                                when a.sign_up_limit = 1 then '截止报名'
                                when t.status = 'sign_up_success' then '报名成功'
                                when t.status = 'sign_up_wait' then '正在审核'
                                when t.status = 'sign_up_full' then '人数已满'
                                when t.status = 'sign_up_fail' then '报名未成功'
                                else '正常报名' 
                            end as sign_up_status,
                            t.status,t.reason,
                            sum( case r.item_type when 'discussion' then 1 else 0 end ) as sign_up,ifnull(v.visits, 0) as visits,
                            case when a.person_id = %s then 1 else 0 end as can_modify 
            from t_discussion as a left join t_codes as m on a.status = m.code_id
            left join (select * from t_traffic where person_id = %s and item_type='discussion') as t on a.id = t.activity_id
            left join (select ifnull(count(v1.id), 0) as visits, 
                visit_target from t_visit as v1, 
                t_discussion as a where v1.visit_target=concat('/page/discussion/', a.id) group by visit_target) as v on v.visit_target=concat('/page/discussion/', a.id)
            left join t_traffic as r on a.id = r.activity_id 
            where a.status!= 'deleted' and activity_start_time >= now() group by a.id order by activity_start_time DESC LIMIT 10 OFFSET """+to_skip,self.current_user,self.current_user)

        yield self.restful(ctx)


@Route(r"/rest/common/discussion/query")
class _(CommonPage):
    @coroutine
    def get(self):
        current_user = self.get_current_user()
        to_skip = self.get_argument('to_skip', '')
        if not to_skip:
            to_skip = 0
        q_word = self.get_argument('q', '')
        q_word = "%%%s%%" % q_word
        ctx = {}
        query = """select a.id, left(published,10) as published,title,pictures,
                                    activity_start_time, activity_end_time,
                                    DATE_FORMAT(activity_start_time, '%%Y年%%m月%%d日') as activity_start_date,
                                    DATE_FORMAT(activity_end_time, '%%Y年%%m月%%d日') as activity_end_date,
                                    DATE_FORMAT(activity_start_time, '%%H:%%i') as activity_start_hm,
                                    DATE_FORMAT(activity_end_time, '%%H:%%i') as activity_end_hm,
                                    m.code_name as status,content,subject,
                                    case 
                                        when a.activity_end_time < now() then '活动已结束' 
                                        else '' 
                                    end as event_time_status,
                                    case 
                                        when a.sign_up_limit = 1 then '截止报名'
                                        when t.status = 'sign_up_success' then '报名成功'
                                        when t.status = 'sign_up_wait' then '正在审核'
                                        when t.status = 'sign_up_full' then '人数已满'
                                        when t.status = 'sign_up_fail' then '报名未成功'
                                        else '正常报名' 
                                    end as sign_up_status,
                                    t.status,t.reason
                    from t_discussion as a left join t_codes as m on a.status = m.code_id
                    left join (select * from t_traffic where person_id = %s and item_type='discussion') as t on a.id = t.activity_id
                    where a.status!= 'deleted' and activity_start_time >= now() and (title like %s or content like %s  or subject like %s ) order by activity_start_time DESC LIMIT 10 OFFSET """+to_skip 
        ctx['discussion'] = yield self.query_db(query,self.current_user,q_word,q_word,q_word)
        yield self.restful(ctx)


@Route(r"/page/requirement/(.*)")
class _(BasePage):
    @assert_user
    @coroutine
    def get(self, id):
        entry = 'requirement_detail'
        page = get_page_by_entry(entry)
        user = self.current_user
        res = yield self.fetchone_db(
            """
               select a.*,
                   u.head_img_url,
                   s.code_name as status_name
               from t_requirement as a
                           left join t_codes as s on s.code_type = 'status' and s.code_id = a.status,
                   t_authorized_user as u
               where a.id = %s and a.auth_id = u.auth_id
               order by a.published DESC limit 0, 1
           """,
            id)
        context = res
        context['allow_reply'] = auth.check_auth(self, roles=['requirement'])
        context['comments'] = yield self.query_db(
            "select r.* , nick_name,head_img_url from t_requirement_comments as r left join t_authorized_user on auth_id=r.mgr_id where requirement_id=%s and r.status!='deleted' order by r.created asc",
            id)
        self.render(page['layout'],
                    entry=entry,
                    page=page,
                    page_config=map_config,
                    context=context)


@Route(r"/common/(requirements)")
class _(CommonPage):
    @assert_user
    @coroutine
    def get_context(self):
        start_id = self.get_argument('start_id', '')
        target = self.get_argument("target", '')
        where = "a.status = 'published'"
        auth_id = ''
        if target == 'mine':
            where = "a.status != 'deleted' and u.auth_id='%s'" % self.current_user
            auth_id = self.current_user
        ctx = {}
        if start_id:
            if target == 'mine':
                ctx['items'] = yield self.query_db(""" select a.*,u.head_img_url,s.code_name as status_name from t_requirement as a 
                    left join t_codes as s on s.code_type = 'status' and s.code_id = a.status 
                    left join t_authorized_user as u on u.auth_id=a.auth_id  left join t_tag on tag_id = subject,
                    t_requirement as b where b.id = %s and a.id <> b.id and a.published < b.published and u.auth_id=%s order by a.published DESC limit 0, 10""",
                                                   start_id, auth_id)
            else:
                ctx['items'] = yield self.query_db(""" select a.*,u.head_img_url,s.code_name as status_name,tag_name from t_requirement as a 
                    left join t_codes as s on s.code_type = 'status' and s.code_id = a.status left join t_authorized_user as u on u.auth_id=a.auth_id 
                    left join t_tag on tag_id = subject ,
                    t_requirement as b where a.status = 'published' and b.id = %s and a.id <> b.id and a.published < b.published order by a.published DESC limit 0, 10""",
                                                   start_id)
        else:
            ctx['items'] = yield self.query_db(
                """
                select a.id, a.title, a.auth_id, a.contact_cellphone, a.contact_name, a.contact_wechatid,
                    a.created, a.updated, a.status, a.intro_content,tag_name,
                    u.head_img_url,
                    s.code_name as status_name
                from t_requirement as a
                        left join t_codes as s on s.code_type = 'status' and s.code_id = a.status 
                        left join t_authorized_user as u on u.auth_id=a.auth_id 
                        left join t_tag on tag_id = subject
                where %s
                order by a.published DESC limit 0, 10
                """ % where)
        raise Return(ctx)


@Route(r"/rest/common/requirements")
class _(CommonPage):
    @assert_user
    @coroutine
    def get(self):
        start_id = self.get_argument('start_id', '')
        target = self.get_argument("target", '')
        where = "a.status = 'published'"
        auth_id = ''
        if target == 'mine':
            where = "u.auth_id='%s'" % self.current_user
            auth_id = self.current_user
        ctx = {}
        if start_id:
            if target == 'mine':
                ctx['items'] = yield self.query_db(""" select a.*,u.head_img_url,s.code_name as status_name from t_requirement as a 
                    left join t_codes as s on s.code_type = 'status' and s.code_id = a.status 
                    left join t_authorized_user as u on u.auth_id=a.auth_id  left join t_tag on tag_id = subject,
                    t_requirement as b where b.id = %s and a.id <> b.id and a.published < b.published and u.auth_id=%s order by a.published DESC limit 0, 10""",
                                                   start_id, auth_id)
            else:
                ctx['items'] = yield self.query_db(""" select a.*,u.head_img_url,s.code_name as status_name,tag_name from t_requirement as a 
                    left join t_codes as s on s.code_type = 'status' and s.code_id = a.status left join t_authorized_user as u on u.auth_id=a.auth_id 
                    left join t_tag on tag_id = subject ,
                    t_requirement as b where a.status = 'published' and b.id = %s and a.id <> b.id and a.published < b.published order by a.published DESC limit 0, 10""",
                                                   start_id)
        else:
            ctx['items'] = yield self.query_db(
                """
                select a.id, a.title, a.auth_id, a.contact_cellphone, a.contact_name, a.contact_wechatid,
                    a.created, a.updated, a.status, a.intro_content,tag_name,
                    u.head_img_url,
                    s.code_name as status_name,a.published
                from t_requirement as a
                        left join t_codes as s on s.code_type = 'status' and s.code_id = a.status 
                        left join t_authorized_user as u on u.auth_id=a.auth_id 
                        left join t_tag on tag_id = subject
                where %s
                order by a.published DESC limit 0, 10
                """ % where)
        yield self.restful(ctx)


@Route(r"/common/(requirements_person)")
class _(CommonPage):
    @assert_user
    @coroutine
    def get_context(self):
        start_id = self.get_argument('start_id', '')
        target = self.get_argument("target", '')
        entry = 'common_requirements_person'
        page = get_page_by_entry(entry)
        auth_id = ''
        where = "a.status != 'deleted' and a.auth_id='%s'" % self.current_user
        auth_id = self.current_user
        ctx = {}
        if start_id:
            ctx['items'] = yield self.query_db(""" select a.*,u.head_img_url,s.code_name as status_name from t_requirement as a 
                left join t_codes as s on s.code_type = 'status' and s.code_id = a.status 
                left join t_authorized_user as u on u.auth_id=a.auth_id  left join t_tag on tag_id = subject,
                t_requirement as b where b.id = %s and  a.status != 'deleted' and a.id <> b.id and a.updated < b.updated and u.auth_id=%s order by a.updated DESC limit 0, 10""",
                                               start_id, auth_id)
        else:
            ctx['items'] = yield self.query_db(
                """
                select a.id, a.title, a.auth_id, a.contact_cellphone, a.contact_name, a.contact_wechatid,
                    a.created, a.updated, a.status, a.intro_content,tag_name,
                    u.head_img_url,
                    s.code_name as status_name
                from t_requirement as a
                        left join t_codes as s on s.code_type = 'status' and s.code_id = a.status 
                        left join t_authorized_user as u on u.auth_id=a.auth_id 
                        left join t_tag on tag_id = subject
                where %s
                order by a.updated DESC limit 0, 10
                """ % where)
        raise Return(ctx)


@Route(r"/rest/common/requirements/person")
class _(CommonPage):
    @assert_user
    @coroutine
    def get(self):
        start_id = self.get_argument('start_id', '')
        auth_id = ''
        where = "a.status != 'deleted' and u.auth_id='%s'" % self.current_user
        auth_id = self.current_user
        ctx = {}
        if start_id:
            ctx['items'] = yield self.query_db(""" select a.*,u.head_img_url,s.code_name as status_name from t_requirement as a 
                left join t_codes as s on s.code_type = 'status' and s.code_id = a.status 
                left join t_authorized_user as u on u.auth_id=a.auth_id  left join t_tag on tag_id = subject,
                t_requirement as b where b.id = %s and  a.status != 'deleted' and a.id <> b.id and a.updated < b.updated and u.auth_id=%s order by a.updated DESC limit 0, 10""",
                                               start_id, auth_id)
        else:
            ctx['items'] = yield self.query_db(
                """
                select a.id, a.title, a.auth_id, a.contact_cellphone, a.contact_name, a.contact_wechatid,
                    a.created, a.updated, a.status, a.intro_content,tag_name,
                    u.head_img_url,
                    s.code_name as status_name
                from t_requirement as a
                        left join t_codes as s on s.code_type = 'status' and s.code_id = a.status 
                        left join t_authorized_user as u on u.auth_id=a.auth_id 
                        left join t_tag on tag_id = subject
                where %s
                order by a.updated DESC limit 0, 10
                """ % where)
        yield self.restful(ctx)


@Route(r"/page/requirement_edit/(.*)")
class _(BasePage):
    @assert_user
    @coroutine
    def get(self, id):
        entry = 'requirement_edit'
        page = get_page_by_entry(entry)
        user = self.current_user
        res = yield self.fetchone_db(
            """
               select a.*,
                   u.head_img_url,
                   s.code_name as status_name
               from t_requirement as a
                           left join t_codes as s on s.code_type = 'status' and s.code_id = a.status,
                   t_authorized_user as u
               where a.id = %s and a.auth_id = u.auth_id
               order by a.published DESC limit 0, 1
           """,
            id)
        context = res
        context['article_sources'] = yield self.query_db(
            "select tag_id , tag_name from t_tag where tag_type='requirement_type'")
        self.render(page['layout'],
                    entry=entry,
                    page=page,
                    page_config=map_config,
                    context=context)


# END COMMON PAGES


# 会员申请表页面
# @Route(r"/appform")
class _(BasePage):
    @coroutine
    def get(self):
        ctx = {'args': {}}

        self.render("layout_common.html",
                    entry="appform",
                    page=get_body_page_by_entry("appform"),
                    page_config=map_config,
                    context=ctx)


# 公示并投票会员申请页面
# @Route(r"/appvote")
class _(BasePage):
    @coroutine
    def get(self):
        ctx = {'args': {}}
        applyid = self.get_argument('id', '')
        yesnum = yield self.fetchone_db("select count(*) as c from dlb_vote where voted_member_id=%s and vote_type=0",
                                        applyid)
        nonum = yield self.fetchone_db("select count(*) as c from dlb_vote where voted_member_id=%s and vote_type=1",
                                       applyid)
        giveupnum = yield self.fetchone_db(
            "select count(*) as c from dlb_vote where voted_member_id=%s and vote_type=2", applyid)
        res1 = yield self.fetchone_db("select * from dlb_person_member where id=%s", applyid)
        if res1:
            if int(res1['gender']) == 0:
                res1['sex'] = "男"
            elif int(res1['gender']) == 1:
                res1['sex'] = "女"
            else:
                res1['sex'] = "未知"

            if int(res1['type']) == 0:
                res1['type'] = '普通'
            elif int(res1['type']) == 1:
                res1['type'] = '理事'
            res1['yes'] = yesnum['c']
            res1['no'] = nonum['c']
            res1['giveup'] = giveupnum['c']
            self.render("layout_common.html",
                        entry="home",
                        page=get_body_page_by_entry("appvoteperson"),
                        page_config=map_config,
                        context=res1)
            return
        res2 = yield self.fetchone_db("select * from dlb_org_member where id=%s", applyid)
        if res2:
            if int(res2['type']) == 0:
                res2['type'] = '普通'
            elif int(res2['type']) == 1:
                res2['type'] = '理事'
            res2['yes'] = yesnum['c']
            res2['no'] = nonum['c']
            res2['giveup'] = giveupnum['c']
            self.render("layout_common.html",
                        entry="home",
                        page=get_body_page_by_entry("appvoteorg"),
                        page_config=map_config,
                        context=res2)
            return


# 会员付费页面
# @Route(r"/apppay")
class _(BasePage):
    @coroutine
    def get(self):
        ctx = {'args': {}}

        self.render("layout_common.html",
                    entry="home",
                    page=get_body_page_by_entry("apppay"),
                    page_config=map_config,
                    context=ctx)


# START LOGIN/LOGOUT PAGES

#
from wechat_sdk import WechatBasic
from util.send_phone_email import send_email


@Route(r"/wechatcheck")
class _(BasePage):
    def report_msg(self, message, wechat):
        # send_email(str(message.id) + " From " + str(message.source), self.config['worker_mail'], message.content, self.config)
        # return
        # send_email(str(message.id) + " From " + str(message.source), "cq@ygh100.com", message.raw, self.config)
        try:
            if message.type not in ['text', 'image']:
                return
            content = {
                'body': '',
                'title': '',
                'picurl': '',
                'created': get_now_str(),
                'user_info': None
            }
            if message.type == 'text':
                content['body'] = message.content
            elif message.type == 'image':
                content['picurl'] = message.picurl
            user_info = wechat.get_user_info(str(message.source))
            # user_info['content'] = message.content
            user_info['icon'] = '<img src="' + user_info['headimgurl'] + '"/>'
            content['title'] = "来自[%s]的消息[%s]" % (user_info['nickname'], str(message.id))
            content['user_info'] = user_info
            res = self.render_string("email_wechat_question.html", content=content)
            send_email(content['title'], self.config['worker_mail'], res, self.config)
        except:
            logging.info("error send message: %s" % str(sys.exc_info()))

    def process(self, wechat, body_text):

        DEFAULT_NEW_RESPONSE = [{
            'title': self.config['wechat_res_title'],
            'picurl': self.config['wechat_res_pic'],
            'description': self.config['wechat_res_desc'],
            'url': self.config['wechat_res_url'],
        }]

        # 对 XML 数据进行解析 (必要, 否则不可执行 response_text, response_image 等操作)
        wechat.parse_data(body_text)
        # 获得解析结果, message 为 WechatMessage 对象 (wechat_sdk.messages中定义)
        message = wechat.get_message()
        response = None
        if message.type == 'subscribe':
            response = wechat.response_news(DEFAULT_NEW_RESPONSE)
        # elif message.type == 'text':
        #     if message.content == 'wechat':
        #         response = wechat.response_text(u'^_^')
        #     else:
        #         response = wechat.response_text(u'哈哈')
        # elif message.type == 'image':
        #     response = wechat.response_text(u'图片')
        else:
            # response = wechat.response_text(self.config['app_welcome'])
            response = wechat.group_transfer_message()

        # self.report_msg(message, wechat)

        return response

    def get(self):
        signature = self.get_argument('signature', '')
        timestamp = self.get_argument('timestamp', '')
        nonce = self.get_argument('nonce', '')
        echostr = self.get_argument('echostr', '')
        token = self.config['wechat_token']
        wechat = WechatBasic(token=token)

        # if self.checksignature(signature, timestamp, nonce):
        if wechat.check_signature(signature=signature, timestamp=timestamp, nonce=nonce):
            self.write(echostr)
        else:
            self.write('fail')

    def post(self):
        signature = self.get_argument('signature', '')
        timestamp = self.get_argument('timestamp', '')
        nonce = self.get_argument('nonce', '')
        echostr = self.get_argument('echostr', '')
        body_text = self.request.body
        token = self.config['wechat_token']
        wechat = WechatBasic(token=token, appid=self.config['wechat_appid'], appsecret=self.config['wechat_secret'],
                             checkssl=False)
        if wechat.check_signature(signature=signature, timestamp=timestamp, nonce=nonce):
            response = self.process(wechat, body_text)
            self.write(response)
        else:
            self.write('fail')


# from flask import Flask, request, abort, render_template
from wechatpy.enterprise.crypto import WeChatCrypto
from wechatpy.exceptions import InvalidSignatureException
from wechatpy.enterprise.exceptions import InvalidCorpIdException
from wechatpy.enterprise import parse_message, create_reply
import xmltodict
from wechatpy.messages import UnknownMessage
from wechatpy.utils import to_text
from wechatpy.enterprise.messages import MESSAGE_TYPES
from wechatpy.enterprise.events import EVENT_TYPES


# 企业号回调
@Route(r"/wechatcorpcheck")
class _(BasePage):
    def report_msg(self, message, wechat):
        # send_email(str(message.id) + " From " + str(message.source), self.config['worker_mail'], message.content, self.config)
        # return
        # send_email(str(message.id) + " From " + str(message.source), "cq@ygh100.com", message.raw, self.config)
        try:
            if message.type not in ['text', 'image']:
                return
            content = {
                'body': '',
                'title': '',
                'picurl': '',
                'created': get_now_str(),
                'user_info': None
            }
            if message.type == 'text':
                content['body'] = message.content
            elif message.type == 'image':
                content['picurl'] = message.picurl
            user_info = wechat.get_user_info(str(message.source))
            # user_info['content'] = message.content
            user_info['icon'] = '<img src="' + user_info['headimgurl'] + '"/>'
            content['title'] = "来自[%s]的消息[%s]" % (user_info['nickname'], str(message.id))
            content['user_info'] = user_info
            res = self.render_string("email_wechat_question.html", content=content)
            send_email(content['title'], self.config['worker_mail'], res, self.config)
        except:
            logging.info("error send message:%s" % str(sys.exc_info()))

    def process(self, wechat, body_text):

        DEFAULT_NEW_RESPONSE = [{
            'title': self.config['wechat_res_title'],
            'picurl': self.config['wechat_res_pic'],
            'description': self.config['wechat_res_desc'],
            'url': self.config['wechat_res_url'],
        }]

        # 对 XML 数据进行解析 (必要, 否则不可执行 response_text, response_image 等操作)
        wechat.parse_data(body_text)
        # 获得解析结果, message 为 WechatMessage 对象 (wechat_sdk.messages中定义)
        message = wechat.get_message()
        response = None
        if message.type == 'subscribe':
            response = wechat.response_news(DEFAULT_NEW_RESPONSE)
        # elif message.type == 'text':
        #     if message.content == 'wechat':
        #         response = wechat.response_text(u'^_^')
        #     else:
        #         response = wechat.response_text(u'哈哈')
        # elif message.type == 'image':
        #     response = wechat.response_text(u'图片')
        else:
            # response = wechat.response_text(self.config['app_welcome'])
            response = wechat.group_transfer_message()

        # self.report_msg(message, wechat)

        return response

    def get(self):
        signature = self.get_argument('msg_signature', '')
        timestamp = self.get_argument('timestamp', '')
        nonce = self.get_argument('nonce', '')
        echo_str = self.get_argument('echostr', '')
        token = self.config['wechat_corp_token']
        wechat = WeChatCrypto(self.config['wechat_corp_token'], self.config['wechat_corp_encodingaeskey'],
                              self.config['wechat_corpid'])
        logging.info("%s,%s,%s" % (
        self.config['wechat_corp_token'], self.config['wechat_corp_encodingaeskey'], self.config['wechat_corpid']))

        try:
            echo_str = wechat.check_signature(
                signature,
                timestamp,
                nonce,
                echo_str
            )
        except InvalidSignatureException:
            self.write('fail')
        logging.info(echo_str)
        self.write(echo_str)

    def parse_chat_message(self, xml):
        if not xml:
            return
        message = xmltodict.parse(to_text(xml))['xml']
        if isinstance(message['Item'], list):
            message_classes = []
            for message in message['Item']:
                message_type = message['MsgType'].lower()
                if message_type == 'event':
                    event_type = message['Event'].lower()
                    message_class = EVENT_TYPES.get(event_type, UnknownMessage)
                else:
                    message_class = MESSAGE_TYPES.get(message_type, UnknownMessage)
                message_classes.append(message_class(message))
            return message_classes
        else:
            message_type = message['Item']['MsgType'].lower()
            if message_type == 'event':
                event_type = message['Item']['Event'].lower()
                message_class = EVENT_TYPES.get(event_type, UnknownMessage)
            else:
                message_class = MESSAGE_TYPES.get(message_type, UnknownMessage)
            return message_class(message['Item'])

    def post(self):
        signature = self.get_argument('msg_signature', '')
        timestamp = self.get_argument('timestamp', '')
        nonce = self.get_argument('nonce', '')
        body_text = self.request.body

        token = self.config['wechat_corp_token']
        wechat = WeChatCrypto(self.config['wechat_corp_token'], self.config['wechat_corp_encodingaeskey'],
                              self.config['wechat_corpid'])
        msg_xml = ""
        try:
            msg_xml = wechat.decrypt_message(
                body_text,
                signature,
                timestamp,
                nonce
            )
        except (InvalidSignatureException, InvalidCorpIdException):
            self.write('fail')
        else:
            logging.info(msg_xml)
            msg = self.parse_chat_message(msg_xml)

        # create reply check one element: msg could be list
        if isinstance(msg, list):
            msg = msg[0]

        if msg and msg.type == 'text':
            message = xmltodict.parse(to_text(msg_xml))['xml']
            PackageId = message['PackageId']
            logging.info(PackageId)
            self.write(PackageId)
            return
        else:
            reply = create_reply('Can not handle this for now', msg).render()

        res = wechat.encrypt_message(reply, nonce, timestamp)
        self.write(res)


# 微信网页扫码登录成功
@Route(r"/wechatweblogin")
class _(BasePage):
    @asynchronous
    @coroutine
    def get(self):
        code = self.get_argument('code', '')
        if not code:
            return
        # 获取accesstoken与openid
        client = tornado.httpclient.AsyncHTTPClient()
        request = tornado.httpclient.HTTPRequest(
            url="https://api.weixin.qq.com/sns/oauth2/access_token?" +
                urllib.urlencode({"appid": self.config['wechat_webid'], "secret": self.config['wechat_websecret'],
                                  "code": code, "grant_type": "authorization_code"}),
            method="GET",
            validate_cert=False
        )
        resp = yield client.fetch(request)
        body = json.loads(resp.body)
        openid = body['openid']
        unionid = body['unionid']
        # refreshtoken=body['refresh_token']
        accesstoken = body['access_token']
        # 获取用户信息
        request = tornado.httpclient.HTTPRequest(
            url="https://api.weixin.qq.com/sns/userinfo?" +
                urllib.urlencode({"access_token": accesstoken, "openid": openid,
                                  "lang": "zh_CN"}),
            method="GET",
            validate_cert=False
        )
        resp = yield client.fetch(request)
        body = json.loads(resp.body)
        # 是否已经授权过
        res = yield self.fetchone_db("""select * from t_person where auth_id=%s""", unionid)
        if not res:
            # 尚未授权过，将用户信息插入授权用户表,同时跳到绑定会员页面
            args = {
                'person_id': generate_uuid(),
                'auth_id': unionid,
                'web_open_id': openid,
                'nick_name': body['nickname'],
                'head_img_url': body['headimgurl'],
                'gender': body['sex'],
                'province': body['province'],
                'city': body['city'],
                'country': body['country'],
                'auth_date': get_now_str()
            }
            yield self.insert_db_by_obj('t_person', args)
        else:
            yield self.update_db("""update t_person 
                                    set web_open_id = %s, auth_date = %s,
                                    nick_name = %s, head_img_url = %s, province = %s, country = %s
                                    where auth_id = %s""",
                                 openid, get_now_str(),
                                 body['nickname'], body['headimgurl'], body['province'], body['country'],
                                 unionid)

        yield auth.login_user(self, unionid)

        redirect_url = self.get_secure_cookie('redirect_url') or '/common'  #
        self.set_secure_cookie('redirect_url', '', 1)
        self.redirect(redirect_url)


# 微信登录成功
@Route(r"/wechatlogin")
class _(BasePage):
    @asynchronous
    @coroutine
    def get(self):
        code = self.get_argument('code', '')
        if not code:
            logging.info('error wechat login')
            return
        # 获取accesstoken与openid
        client = tornado.httpclient.AsyncHTTPClient()
        request = tornado.httpclient.HTTPRequest(
            url="https://api.weixin.qq.com/sns/oauth2/access_token?" +
                urllib.urlencode({"appid": self.config['wechat_appid'], "secret": self.config['wechat_secret'],
                                  "code": code, "grant_type": "authorization_code"}),
            method="GET",
            validate_cert=False
        )
        resp = yield client.fetch(request)
        body = json.loads(resp.body)
        logging.info(body)
        openid = body['openid']
        unionid = body.get('unionid')

        accesstoken = body['access_token']

        # 获取用户信息
        request = tornado.httpclient.HTTPRequest(
            url="https://api.weixin.qq.com/sns/userinfo?" +
                urllib.urlencode({"access_token": accesstoken, "openid": openid,
                                  "lang": "zh_CN"}),
            method="GET",
            validate_cert=False
        )
        resp = yield client.fetch(request)
        body = json.loads(resp.body)
        #判断有没有unionid,只有服务号用服务号登录
        if unionid:
            # 是否已经授权过
            res = yield self.fetchone_db("""select * from t_person where auth_id=%s""", unionid)
            if not res:
                # 尚未授权过，将用户信息插入授权用户表,同时跳到绑定会员页面
                args = {
                    'person_id': generate_uuid(),
                    'auth_id': unionid,
                    'open_id': openid,
                    'nick_name': body['nickname'],
                    'head_img_url': body['headimgurl'],
                    'gender': body['sex'],
                    'province': body['province'],
                    'city': body['city'],
                    'country': body['country'],
                    'auth_date': get_now_str()
                }
                yield self.insert_db_by_obj('t_person', args)
            else:
                yield self.update_db("""update t_person 
                                        set open_id = %s, auth_date = %s,
                                        nick_name = %s, head_img_url = %s, province = %s, country = %s
                                        where auth_id = %s""",
                                     openid, get_now_str(),
                                     body['nickname'], body['headimgurl'], body['province'], body['country'],
                                     unionid)
            yield auth.login_user(self, union_id=unionid)
        else:
            # 是否已经授权过
            res = yield self.fetchone_db("""select * from t_person where open_id=%s""", openid)
            if not res:
                # 尚未授权过，将用户信息插入授权用户表,同时跳到绑定会员页面
                args = {
                    'person_id': generate_uuid(),
                    'open_id': openid,
                    'nick_name': body['nickname'],
                    'head_img_url': body['headimgurl'],
                    'gender': body['sex'],
                    'province': body['province'],
                    'city': body['city'],
                    'country': body['country'],
                    'auth_date': get_now_str()
                }
                yield self.insert_db_by_obj('t_person', args)
            else:
                yield self.update_db("""update t_person 
                                        set  auth_date = %s,
                                        nick_name = %s, head_img_url = %s, province = %s, country = %s
                                        where open_id = %s""",
                                     get_now_str(),
                                     body['nickname'], body['headimgurl'], body['province'], body['country'],
                                     openid)
            yield auth.login_user(self, open_id=openid)
        

        redirect_url = self.get_secure_cookie('redirect_url') or '/common'  #
        self.set_secure_cookie('redirect_url', '', 1)

        self.redirect(redirect_url)


# 用户登录
@Route(r"/login")
class _(BasePage):
    @coroutine
    def get_corp_login(self):
        logging.info("host:%s" % self.request.host)
        if self.request.host == "hero.tsingdata.com":
            url = 'https://open.weixin.qq.com/connect/oauth2/authorize?appid=' + self.config[
                'wechat_corpid'] + '&redirect_uri=http%3A%2F%2F' + self.request.host + '%2Fwechatcorplogin&response_type=code&scope=snsapi_base&state=STATE#wechat_redirect'
        else:
            url = 'https://open.weixin.qq.com/connect/oauth2/authorize?appid=' + self.config[
                'wechat_corpid'] + '&redirect_uri=https%3A%2F%2F' + self.request.host + '%2Fwechatcorplogin&response_type=code&scope=snsapi_base&state=STATE#wechat_redirect'
        # url = 'https://open.weixin.qq.com/connect/qrconnect?appid=' + self.config['wechat_webid'] + '&redirect_uri=http%3A%2F%2F' + self.request.host + '%2Fwechatweblogin&response_type=code&scope=snsapi_login&state=STATE#wechat_redirect'
        self.redirect(url)
        raise Return(True)

    @coroutine
    def get_webscan_login(self):
        url = 'https://open.weixin.qq.com/connect/qrconnect?appid=' + self.config[
            'wechat_webid'] + '&redirect_uri=http%3A%2F%2F' + self.request.host + '%2Fwechatweblogin&response_type=code&scope=snsapi_login&state=STATE#wechat_redirect'
        self.redirect(url)
        raise Return(True)

    @coroutine
    def get_wechat_login(self):
        url = 'https://open.weixin.qq.com/connect/oauth2/authorize?appid=' + self.config[
            'wechat_appid'] + '&redirect_uri=http%3A%2F%2F' + self.request.host + '%2Fwechatlogin&response_type=code&scope=snsapi_userinfo&state=STATE#wechat_redirect'
        self.redirect(url)
        raise Return(True)

    @coroutine
    def get_mockup_login(self):
        uuid = self.get_argument('uuid', '')
        pwd = self.get_argument('uupwd', '')
        if uuid and pwd == settings['cipher'] and (settings['debug'] or self.request.host.startswith('test-')):
            usr = yield self.fetchone_db(
                """select * from t_person where (person_id=%s or corp_open_id=%s or auth_id = %s or cellphone=%s or email=%s)""",
                uuid, uuid, uuid, uuid, uuid)
            if not usr:
                # 尚未授权过，将用户信息插入授权用户表,同时跳到绑定会员页面
                tpuuid = generate_uuid()
                args = {
                    'person_id': tpuuid,
                    'auth_id': tpuuid,
                    'open_id': tpuuid,
                    'nick_name': '测试' + str(1000 + random.randint(1, 999)),
                    'head_img_url': 'http://wx.qlogo.cn/mmopen/2kpMNDYsSfDrf9ZwO6wVUYSZlwgZUqC9yZxgrP8oR6aR91sXKUoUfWlFkwm8oW5hL7hoiaxlWqA5a4r6YXvlUWQ/0',
                    'gender': 1,
                    'province': '北京',
                    'city': '海淀',
                    'country': '中国',
                    'auth_date': get_now_str()
                }
                yield self.insert_db_by_obj('t_person', args)
                yield auth.login_user(self, tpuuid)
            else:
                res = yield self.fetchone_db("""select * from t_person where person_id=%s""", usr.person_id)
                if res:
                    yield auth.login_user(self, person_id=usr.person_id)
                    raise Return(True)
                    return
                else:
                    raise Return(False)
                    return
                    # res = yield self.fetchone_db("""select * from t_person where auth_id=%s""",uuid)
                    # if res:
                    #     yield auth.login_user(self,union_id= uuid)
                    #     raise Return(True)
                    #     return
                    # res = yield self.fetchone_db("""select * from t_person where corp_open_id=%s""",uuid)
                    # if res:
                    #     yield auth.login_user(self,corp_open_id= uuid)
                    #     raise Return(True)
                    #     return

            raise Return(True)
        raise Return(False)

    @coroutine
    def get_mockup_login_uuid(self):
        uuid = self.get_argument('uuid', '')
        if uuid:
            usr = yield self.fetchone_db(
                """select * from t_person where (person_id=%s or corp_open_id=%s or auth_id = %s or cellphone=%s or email=%s)""",
                uuid, uuid, uuid, uuid, uuid)
            if not usr:
                # 尚未授权过，将用户信息插入授权用户表,同时跳到绑定会员页面
                tpuuid = generate_uuid()
                args = {
                    'person_id': tpuuid,
                    'auth_id': tpuuid,
                    'open_id': tpuuid,
                    'nick_name': '测试' + str(1000 + random.randint(1, 999)),
                    'head_img_url': 'http://wx.qlogo.cn/mmopen/2kpMNDYsSfDrf9ZwO6wVUYSZlwgZUqC9yZxgrP8oR6aR91sXKUoUfWlFkwm8oW5hL7hoiaxlWqA5a4r6YXvlUWQ/0',
                    'gender': 1,
                    'province': '北京',
                    'city': '海淀',
                    'country': '中国',
                    'auth_date': get_now_str()
                }
                yield self.insert_db_by_obj('t_person', args)
                yield auth.login_user(self, tpuuid)
            else:
                res = yield self.fetchone_db("""select * from t_person where person_id=%s""", usr.person_id)
                if res:
                    yield auth.login_user(self, person_id=usr.person_id)
                    raise Return(True)
                    return
                else:
                    raise Return(False)
                    return

            raise Return(True)
        raise Return(False)

    @coroutine
    def post(self):
        res = yield self.get_mockup_login()
        if res:
            self.redirect(self.get_secure_cookie('redirect_url') or '/common')
        else:
            self.redirect('/page/mockuplogin')

    @coroutine
    def get(self):

        url = self.get_argument('redirect_url', '') or self.get_secure_cookie('redirect_url')
        if url:
            self.set_secure_cookie('redirect_url', url)
        else:
            url = '/common'

        if settings['debug']:
            res = self.get_argument('uuid', '')
            if res:
                res = yield self.get_mockup_login_uuid()
                if res:
                    self.redirect(self.get_secure_cookie('redirect_url') or '/common')

        if self.is_wechat():
            corp = self.config['wechat_corp_auth']
            if corp == '1':
                res = yield self.get_corp_login()
            else:
                res = yield self.get_wechat_login()
        else:
            yield self.get_webscan_login()


@Route(r"/logout")
class _(BasePage):
    @coroutine
    def get(self):
        res, msg = yield auth.logout_user(self)
        entry = 'logout'
        page = get_page_by_entry(entry)

        self.render(page['layout'],
                    entry=entry,
                    page=page,
                    page_config=map_config,
                    context=None)

    # END LOGIN/LOGOUT PAGES


# 会员投票
@Route(r"/page/form_vote_(.*)")
class _(BasePage):
    @preassert_user
    @coroutine
    def get(self, form_id):
        entry = 'form_vote'
        page = get_page_by_entry(entry)
        ctx = dict()
        ctx['no_cellphone'] = False
        ctx['no_login'] = False
        ctx['form_id'] = form_id
        if not self.current_user:
            ctx['no_login'] = True
            self.render(page['layout'],
                        entry=entry,
                        page=page,
                        page_config=map_config,
                        context=ctx)
        yield auth.login_user(self, person_id=self.current_user)
        if self.current_user_profile and not self.current_user_profile['person']['cellphone']:
            ctx['no_cellphone'] = True
            self.render(page['layout'],
                        entry=entry,
                        page=page,
                        page_config=map_config,
                        context=ctx)
        yield auth.login_user(self, person_id=self.current_user)
        res = yield self.fetchone_db('''
            select a.form_code,a.apply_member_type,a.form_id,a.apply_date,a.form_status,
                    a.form_status,b.code_name as apply_member_type_name,o.*,
                    p.*,c.code_name as form_status_name
            from 
            t_form as a
            LEFT JOIN t_codes as b ON b.code_type = 'member_type' and b.code_id = a.apply_member_type
            LEFT JOIN t_codes as c ON c.code_type = 'form_status' and c.code_id = a.form_status,                                                       
            t_org as o, t_form_relation as fr, 
            t_org_person as op 
            LEFT JOIN t_person as p on p.person_id = op.person_id
            where 
            a.form_status <> 'deleted' 
            and fr.form_id = a.form_id 
            and fr.org_id = o.org_id
            and op.is_primary = 1
            and op.org_id = o.org_id
            and a.form_id = %s
            ''', form_id)
        if not res:
            res = yield self.fetchone_db('''
                        select a.form_code,a.apply_member_type,a.form_id,a.apply_date,a.form_status,
                                a.form_status,b.code_name as apply_member_type_name,o.*,
                                p.*,c.code_name as form_status_name
                        from
                        t_form as a
                        LEFT JOIN t_codes as b ON b.code_type = 'member_type' and b.code_id = a.apply_member_type
                        LEFT JOIN t_codes as c ON c.code_type = 'form_status' and c.code_id = a.form_status,
                        t_org as o, t_form_relation as fr,
                        t_org_person as op
                        LEFT JOIN t_person as p on p.person_id = op.person_id
                        where
                        a.form_status <> 'deleted'
                        and fr.form_id = a.form_id
                        and fr.person_id = p.person_id
                        and op.is_primary = 0
                        and op.org_id = o.org_id
                        and a.form_id = %s
                        ''', form_id)

        if self.current_user and self.current_user_profile and self.current_user_profile['person']['cellphone']:
            if res['apply_member_type'] in ['normal_member', 'normal_org_member']:
                if not auth.check_auth(self, roles=['admin', 'master', 'operator']) and not auth.check_auth(self,
                                                                                                            is_member=True):
                    yield self.redirect_unauth()
                    return
            elif res['apply_member_type'] in ['advanced_member', 'advanced_org_member']:
                if not auth.check_auth(self, roles=['admin', 'master', 'operator']) and not auth.check_auth(self,
                                                                                                            members=[
                                                                                                                'advanced_member',
                                                                                                                'advanced_org_member']):
                    yield self.redirect_unauth()
                    return

        number = {}
        if res['apply_member_type'] in ['normal_member', 'normal_org_member']:
            number = yield self.fetchone_db(
                "select count(1) as number from t_vote_record as v , t_auth_role as r where r.role_id='master' and r.auth_id=v.auth_id and v.form_id=%s and v.attitue='agree'",
                form_id)
        elif res['apply_member_type'] in ['advanced_member', 'advanced_org_member']:
            count = yield self.fetchone_db(
                "select sum(case attitue when 'agree' then 1 else 0 end) as agree ,sum(case attitue when 'oppose' then 1 else 0 end) as oppose,sum(case attitue when 'waive' then 1 else 0 end) as waive from t_vote_record where form_id=%s",
                form_id)
            total = yield self.fetchone_db(
                "select count(1) as total from t_member where member_type='advanced_member' or member_type='advanced_org_member'")
            mishu = yield self.fetchone_db(
                "select count(1) as mishu from t_auth_role as r  where r.role_id='master' and r.auth_id not in (select auth_id from t_member where member_type = 'advanced_org_member' or member_type='advanced_member')")
            total = total['total'] + mishu['mishu']
            agree = 0
            oppose = 0
            waive = 0
            not_yet = 0
            if total:
                agree = ((count['agree'] or 0) / total) * 100
                oppose = ((count['oppose'] or 0) / total) * 100
                waive = ((count['waive'] or 0) / total) * 100
                not_yet = 100 - agree - oppose - waive
            number = {
                'agree': "%s%s" % ('%.2f' % agree, "%"),
                'oppose': "%s%s" % ('%.2f' % oppose, "%"),
                'waive': "%s%s" % ('%.2f' % waive, "%"),
                'not_yet': "%s%s" % ('%.2f' % not_yet, "%")
            }
        if res['apply_member_type'] in ['normal_org_member', 'advanced_org_member']:
            person = yield self.query_db(
                "select p.* , op.is_primary from t_person as p left join t_form_relation as r on p.person_id = r.person_id left join t_org_person as op on op.person_id = r.person_id where r.form_id = %s order by op.is_primary",
                form_id)
            ctx = {'form': res, 'number': number, 'person': person}
        else:
            ctx = {'form': res, 'number': number}
        page = get_page_by_entry(entry)
        ctx['form_id'] = form_id
        ctx['no_cellphone'] = False
        ctx['no_login'] = False
        self.render(page['layout'],
                    entry=entry,
                    page=page,
                    page_config=map_config,
                    context=ctx)


@Route(r"/page/delivery_info_(.*)")
class _(BasePage):
    @assert_user
    @coroutine
    def get(self, person_id):
        entry = 'delivery_info'
        res = yield self.fetchone_db('''
            select p.fullname , p.gender , p.school,p.education,p.person_info,p.expects,p.wills,p.position,p.weixin_group,
            o.org_name,p.wechatid,
            o.general_description,o.domain_description,o.website
            from t_person as p , t_org as o ,t_org_person as op
            where p.person_id = op.person_id and op.org_id = o.org_id and p.person_id = %s
            ''', person_id)
        page = get_page_by_entry(entry)
        ctx = {}
        ctx['form'] = res

        page['share_title'] = '%s的个人名片' % res['fullname']
        page['share_description'] = '%s %s %s %s' % (
        res['position'], res['org_name'], res['school'], res['general_description'])

        self.render(page['layout'],
                    entry=entry,
                    page=page,
                    page_config=map_config,
                    context=ctx)


@Route(r"/page/wechat_info_(.*)")
class _(BasePage):
    @assert_user
    @coroutine
    def get(self, auth_id):
        entry = 'wechat_info'
        res = yield self.fetchone_db('''
            select * from t_person where person_id = %s
            ''', auth_id)
        page = get_page_by_entry(entry)
        ctx = {}
        ctx['form'] = res
        self.render(page['layout'],
                    entry=entry,
                    page=page,
                    page_config=map_config,
                    context=ctx)


@Route(r"/page/article/(.*)")
class _(BasePage):
    @coroutine
    def get(self, id):
        entry = 'article_detail'
        page = get_page_by_entry(entry)
        ctx = yield self.fetchone_db("""select left(published,10) as published,content,title,pictures,data_source,data_type,subject,
                                        t_tag.tag_name as data_source_name, t_tag.tag_url as data_source_url,
                                        t_tag.tag_icon as data_source_icon
                                        from t_article left join t_tag on t_tag.tag_id = t_article.subject and t_tag.tag_type = 'article_source'
                                         where id = %s""", id)

        page['share_title'] = ctx['title']
        page['share_description'] = html2text.html2text(ctx['content']).strip()[:50].replace('\n', '')
        page['share_icon'] = self.config['site_host_url'] + 'assets/ticket/image/' + str(ctx['pictures']).split(',')[0]

        self.render(page['layout'],
                    entry=entry,
                    page=page,
                    page_config=map_config,
                    context=ctx)


@Route(r"/page/event/(.*)")
class _(BasePage):
    @preassert_user
    @coroutine
    def get(self, id):
        entry = 'event_detail'
        page = get_page_by_entry(entry)
        user = self.current_user
        logging.info("user:%s" % user)
        uuid = self.get_argument('uuid', '')
        uukey = self.get_argument('uukey', '')
        signin=self.get_argument('signin','')#用来控制授权后，是否还跳转到签到页
        if not user and uuid and uukey and self.get_cache(uukey) == uuid:
            logging.info("redirect to login_user:%s" % uuid)
            yield auth.login_user(self, person_id=uuid)
            user = self.get_current_user()
            self.redirect('/page/event/' + str(id) + '?reload=1')
            return
        if user and not self.current_user_profile:
            res = yield auth.login_user(self, person_id=user)
            if res:
                user = self.get_current_user()
                self.redirect('/page/event/' + str(id) + '?reload=1')
            return

        ctx = yield self.fetchone_db("""select id, left(published,10) as published,content,title,pictures,data_source,signup_content,sign_up_limit,
                                        activity_start_time, activity_end_time,activity_guider,
                                        activity_sponsor,activity_undertake,activity_organizer,
                                        co.code_name as activity_online_offline,c.code_name as activity_type,paid,
                                        activity_place,general_place,
                                        DATE_FORMAT(activity_start_time, '%%Y年%%m月%%d日') as activity_start_date,
                                        DATE_FORMAT(activity_end_time, '%%Y年%%m月%%d日') as activity_end_date,
                                        DATE_FORMAT(activity_start_time, '%%H:%%i') as activity_start_hm,
                                        DATE_FORMAT(activity_end_time, '%%H:%%i') as activity_end_hm,
                                        sign_up_fields,
                                        sur_id,
                                        status,
                                        event_corp_auth
                                        from t_news as t
                                        left join t_codes as co on t.activity_online_offline = co.code_id 
                                        left join t_codes as c on t.activity_type = c.code_id 
                                         where id = %s""", id)
        if not ctx:
            self.redirect('/404?page=' + self.request.uri)
            return

        if user:
            register = yield self.fetchone_db(
                "select created from t_traffic where activity_id = %s and person_id = %s and item_type='register'", id,
                user)
            sign_up = yield self.fetchone_db(
                "select created ,code_name ,status ,reason, contribution, is_volunteer from t_traffic left join t_codes on code_id=status where activity_id = %s and person_id = %s and item_type='sign_up' AND status!='deleted'",
                id, user)
        else:
            register = None
            sign_up = None
        context = {}
        # 判断活动是否结束，用以显示活动结束按钮
        if (datetime.datetime.today() > ctx['activity_end_time']):
            context['show_over_button'] = True
        else:
            context['show_over_button'] = False
        context['activity'] = ctx
        if ctx['sur_id']:
            context['survey'] = yield get_survey(self, ctx['sur_id'], user)
        context['register'] = register
        context['sign_up'] = sign_up
        context['status'] = {}
        time = datetime.datetime.today()
        if ctx['activity_end_time'] > time and ctx['sign_up_limit'] == 0:
            context['status']['sign_up'] = True
        else:
            context['status']['sign_up'] = False
        startTime = ctx['activity_start_time']
        d2 = startTime - datetime.timedelta(hours=1)
        endTime = ctx['activity_end_time']
        if time > d2 and time < endTime:
            context['status']['register'] = True
        else:
            context['status']['register'] = False

        page['share_title'] = context['activity']['title']
        page['share_description'] = html2text.html2text(context['activity']['content']).strip()[:50].replace('\n',
                                                                                                             '').replace(
            '#', '')
        page['share_icon'] = self.config['site_host_url'] + 'assets/ticket/image/' + \
                             str(context['activity']['pictures']).split(',')[0]
        context['user_profile'] = self.current_user_profile
        page['title'] = context['activity']['title']
        context['signin']=signin #用来控制授权后，是否还跳转到签到页
        # visit track
        if user:
            try:
                yield track_visit(self, user, '/page/event/%s' % id)
            except:
                logging.info('track error')

        self.render(page['layout'],
                    entry=entry,
                    page=page,
                    page_config=map_config,
                    context=context)

@Route(r"/page/discussion/(.*)")
class _(BasePage):
    @preassert_user
    @coroutine
    def get(self, id):
        entry = 'discussion_detail'
        page = get_page_by_entry(entry)
        user = self.current_user
        logging.info("user:%s" % user)
        uuid = self.get_argument('uuid', '')
        uukey = self.get_argument('uukey', '')
        if not user and uuid and uukey and self.get_cache(uukey) == uuid:
            logging.info("redirect to login_user:%s" % uuid)
            yield auth.login_user(self, person_id=uuid)
            user = self.get_current_user()
            self.redirect('/page/discussion/' + str(id) + '?reload=1')
            return
        if user and not self.current_user_profile:
            res = yield auth.login_user(self, person_id=user)
            if res:
                user = self.get_current_user()
                self.redirect('/page/discussion/' + str(id) + '?reload=1')
            return

        ctx = yield self.fetchone_db("""select id, left(published,10) as published,content,title,pictures,signup_content,sign_up_limit,
                                        activity_start_time, activity_end_time,subject,
                                        co.code_name as activity_online_offline,c.code_name as activity_type,
                                        DATE_FORMAT(activity_start_time, '%%Y年%%m月%%d日') as activity_start_date,
                                        DATE_FORMAT(activity_end_time, '%%Y年%%m月%%d日') as activity_end_date,
                                        DATE_FORMAT(activity_start_time, '%%H:%%i') as activity_start_hm,
                                        DATE_FORMAT(activity_end_time, '%%H:%%i') as activity_end_hm,
                                        sign_up_fields,sign_up_limit
                                        from t_discussion as t
                                        left join t_codes as co on t.activity_online_offline = co.code_id 
                                        left join t_codes as c on t.activity_type = c.code_id 
                                         where id = %s""", id)
        if not ctx:
            self.redirect('/404?page=' + self.request.uri)
            return

        if user:
            # register = yield self.fetchone_db(
            #     "select created from t_traffic where activity_id = %s and person_id = %s and item_type='discussion'", id,
            #     user)
            register = None
            sign_up = yield self.fetchone_db(
                "select created ,code_name ,status ,reason, contribution, is_volunteer from t_traffic left join t_codes on code_id=status where activity_id = %s and person_id = %s and item_type='discussion'",
                id, user)
        else:
            register = None
            sign_up = None
        context = {}
        # 判断活动是否结束，用以显示活动结束按钮
        if (datetime.datetime.today() > ctx['activity_end_time']):
            context['show_over_button'] = True
        else:
            context['show_over_button'] = False
        context['activity'] = ctx
        context['register'] = register
        context['sign_up'] = sign_up
        context['status'] = {}
        time = datetime.datetime.today()
        if ctx['activity_end_time'] > time and ctx['sign_up_limit'] == 0:
            context['status']['sign_up'] = True
        else:
            context['status']['sign_up'] = False
        startTime = ctx['activity_start_time']
        d2 = startTime - datetime.timedelta(hours=1)
        endTime = ctx['activity_end_time']
        if time > d2 and time < endTime:
            context['status']['register'] = True
        else:
            context['status']['register'] = False

        page['share_title'] = context['activity']['title']
        page['share_description'] = html2text.html2text(context['activity']['content']).strip()[:50].replace('\n','').replace('#', '')
        page['share_icon'] = self.config['site_host_url'] + 'assets/ticket/image/' + \
                             str(context['activity']['pictures']).split(',')[0]
        context['user_profile'] = self.current_user_profile
        page['title'] = context['activity']['title']

        # visit track
        if user:
            try:
                yield track_visit(self, user, '/page/discussion/%s' % id)
            except:
                logging.info('track error')

        self.render(page['layout'],
                    entry=entry,
                    page=page,
                    page_config=map_config,
                    context=context)

@Route(r"/page/survey/(.*)")
class _(BasePage):
    @preassert_user
    @coroutine
    def get(self, id):
        entry = 'survey_detail'
        page = get_page_by_entry(entry)
        user = self.current_user

        survey = yield get_survey(self, id, user or self.get_secure_cookie(id))

        page['share_title'] = survey['title']
        page['share_description'] = html2text.html2text(survey['content'] or survey['title']).strip()[:50].replace('\n',
                                                                                                                   '').replace(
            '#', '')
        page['share_icon'] = self.config['site_host_url'] + 'assets/ticket/image/' + str(survey['image']).split(',')[0]

        context = {
            'survey': survey,
            'user_profile': self.current_user_profile
        }

        # visit track
        if user:
            try:
                yield track_visit(self, user, '/page/survey/%s' % id)
            except:
                logging.info('track error')

        if 'submit' in survey:
            page['tpl'] = page['tpl'].replace('.html', '_done.html')
        self.render(page['layout'],
                    entry=entry,
                    page=page,
                    page_config=map_config,
                    context=context)

    @preassert_user
    @coroutine
    def post(self, id):
        user = self.current_user

        res = yield post_survey(self, id, user)
        if res != True:
            yield self.error(res['error'])
            return

        yield self.success("恭喜你，提交成功！")


@Route(r"/page/activity")
class _(BasePage):
    @assert_user
    @coroutine
    def get(self):
        entry = 'activity_detail'
        id = self.get_argument('id')
        page = get_page_by_entry(entry)
        user = self.current_user_profile
        ctx = yield self.fetchone_db(
            "select id, left(published,10) as published,content,title,pictures,data_source,activity_start_time,activity_end_time,activity_sponsor,activity_undertake from t_news where id = %s",
            id)
        register = yield self.fetchone_db(
            "select created from t_traffic where activity_id = %s and person_id = %s and item_type='register'", id,
            user['authorized']['person_id'])
        sign_up = yield self.fetchone_db(
            "select created from t_traffic where activity_id = %s and person_id = %s and item_type='sign_up'", id,
            user['authorized']['person_id'])
        context = {}
        context['activity'] = ctx
        context['register'] = register
        context['sign_up'] = sign_up

        self.render(page['layout'],
                    entry=entry,
                    page=page,
                    page_config=map_config,
                    context=context)


@Route(r"/page/form_paid_(.*)")
class _(BasePage):
    @coroutine
    def get(self, form_id):
        entry = 'form_paid'
        res = yield self.fetchone_db('''
            select a.form_code,a.apply_member_type,a.form_id,a.apply_date,a.form_status,
                    a.form_status,b.code_name as apply_member_type_name,o.org_name,
                    p.fullname,c.code_name as form_status_name
            from 
            t_form as a
            LEFT JOIN t_codes as b ON b.code_type = 'member_type' and b.code_id = a.apply_member_type
            LEFT JOIN t_codes as c ON c.code_type = 'form_status' and c.code_id = a.form_status,                                                       
            t_org as o, t_form_relation as fr, 
            t_org_person as op 
            LEFT JOIN t_person as p on p.person_id = op.person_id
            where 
            a.form_status <> 'deleted' 
            and fr.form_id = a.form_id 
            and fr.org_id = o.org_id
            and op.is_primary = 1
            and op.org_id = o.org_id
            and a.form_id = %s
            ''', form_id)
        ctx = {'form': res}
        page = get_page_by_entry(entry)

        self.render(page['layout'],
                    entry=entry,
                    page=page,
                    page_config=map_config,
                    context=ctx)


@Route(r"/page/form_submitted")
class _(BasePage):
    @coroutine
    def get(self):
        entry = 'form_submitted'
        page = get_page_by_entry(entry)
        user = self.current_user_profile
        context = {}
        context['type'] = self.get_argument("type", "")
        self.render(page['layout'],
                    entry=entry,
                    page=page,
                    page_config=map_config,
                    context=context)


@Route(r"/page/form_fail")
class _(BasePage):
    @coroutine
    def get(self):
        entry = 'form_fail'
        page = get_page_by_entry(entry)
        user = self.current_user_profile
        self.render(page['layout'],
                    entry=entry,
                    page=page,
                    page_config=map_config,
                    context=None)


# 微信群友申请
@Route(r"/page/weixin_group")
class _(MgrHandler):
    @coroutine
    def post(self):
        apply_member_type = "weixin_group"
        person_args = self.get_args({
            'auth_id': '',
            'open_id': '',
            'fullname': '*',
            'gender': '*',
            'cellphone': '*',
            'email': '*',
            'address': '*',
            'school': '*',
            'school_start': '*',
            'education': '*',
            'person_info': '*',
            'birthday': '*',
            'city': '*',
            'wechatid': '*',
            'position': '*',
            'expects': '*',
            'wills': '*',
            'weixin_group': '*',
            'attachment': '',
            'school_number': '',
            'school_department': '',
            'first_normal_recommend': '',
            'second_normal_recommend': ''
        })
        if not person_args:
            yield self.error('miss_param')
            return
        org_args = self.get_args({
            'org_name': '*',
            'general_description': '*',
            'domain_description': '*',
            'website': '',
            'industry': '*',
            'office_address': '',
            'high_tech': '',
            'comments': ''
        })
        if not org_args:
            yield self.error('miss_param')
            return

        # 如果t_title已存在相关职位,则取出title_id插入t_org_person,如果未存在则在t_title创建记录,再插入t_org_person
        title_id = ''
        res_title_name = yield self.fetchone_db("select * from t_title where title_name = '{title_name}'".format(
            title_name=person_args['position']))
        if not res_title_name:
            res_id = yield self.fetchone_db("select max(title_id)+1 as max_id from t_title")
            max_id = res_id['max_id']
            yield self.insert_db(
                "insert into t_title (title_id,title_name) value ('{title_id}','{title_name}')".format(
                    title_id=max_id, title_name=person_args['position']))
            title_id = str(max_id)
        else:
            title_id = res_title_name['title_id']

        # 如果申请人手机号 or 邮箱相同,则可以判断为同一个人
        person_info = yield self.fetchone_db(
            "select * from t_person where cellphone='{cellphone}' or email='{email}'".format(
                cellphone=person_args['cellphone'], email=person_args['email']))

        # 如果在t_person里面有记录
        if person_info:
            person_args['person_id'] = person_info['person_id']
            person_res = yield self.update_db_by_obj('t_person', person_args,
                                                     "person_id='%s'" % person_args['person_id'])
            f_form_info = yield self.fetchone_db(
                """select f.form_id as f_form_id,fr.form_id from t_form_relation as fr left join t_form as f on f.form_id = fr.form_id where f.apply_member_type = '{apply_member_type}' and person_id = '{person_id}'""".format(
                    apply_member_type=apply_member_type, person_id=person_args['person_id']))
            # 如果已经申请过微信群友
            if f_form_info and f_form_info['f_form_id']:
                logging.info('Reapply for %s' % apply_member_type)
                org_res = yield self.fetchone_db("select org_id from t_org where org_name = %s",
                                                 org_args['org_name'])
                if not org_res:
                    org_args['org_id'] = generate_uuid()
                    yield self.insert_db_by_obj('t_org', org_args)
                    org_person_args = {
                        'person_id': person_args['person_id'],
                        'org_id': org_args['org_id'],
                        'is_primary': 0,
                        'title_id': int(title_id)
                    }
                    t_form_args = {
                        'form_id': f_form_info['form_id'],
                        'update_date': get_now_str()
                    }
                    yield self.insert_db_by_obj('t_org_person', org_person_args)
                    yield self.update_db_by_obj('t_form', t_form_args, "form_id='%s'" % t_form_args['form_id'])
                else:
                    org_person = yield self.fetchone_db(
                        "select * from t_org_person where org_id = %s and person_id = %s",
                        org_res['org_id'], person_args['person_id'])
                    org_args['org_id'] = org_res['org_id']
                    org_person_args = {
                        'person_id': person_args['person_id'],
                        'org_id': org_args['org_id'],
                        'is_primary': 0,
                        'title_id': int(title_id)
                    }
                    t_form_args = {
                        'form_id': f_form_info['form_id'],
                        'update_date': get_now_str()
                    }
                    if not org_person:
                        yield self.insert_db_by_obj('t_org_person', org_person_args)
                    else:
                        yield self.update_db(
                            """update t_org_person set title_id = %d where person_id='%s' and org_id='%s'""" % (
                                int(title_id), person_args['person_id'], org_args['org_id']))
                    yield self.update_db_by_obj('t_form', t_form_args, "form_id='%s'" % t_form_args['form_id'])
                    yield self.update_db_by_obj('t_org', org_args, "org_id='%s'" % org_args['org_id'])
                    self.restful({"page": "/page/form_submitted"})
                    return
                    # 如果person_id为空
        else:
            person_args['person_id'] = generate_uuid()
            person_args['weixin_created'] = get_now_str()
            person_res = yield self.insert_db_by_obj('t_person', person_args)
        org_person = yield self.query_db("select * from t_org_person where person_id=%s ", person_args['person_id'])
        if org_person:
            org_args['org_id'] = org_person[0]['org_id']
            yield self.update_db_by_obj('t_org', org_args, "org_id='%s'" % org_args['org_id'])
        else:
            org_args['org_id'] = generate_uuid()
            org_res = yield self.insert_db_by_obj('t_org', org_args)
            org_person_args = {
                'person_id': person_args['person_id'],
                'org_id': org_args['org_id'],
                'is_primary': 0,
                'title_id': int(title_id)
            }
            person_org_res = yield self.insert_db_by_obj('t_org_person', org_person_args)
        form_rel_args = {
            'form_id': generate_uuid(),
            'person_id': person_args['person_id'],
            'org_id': ''
        }
        form_rel_res = yield self.insert_db_by_obj('t_form_relation', form_rel_args)
        # 预设会员费
        res = yield self.fetchone_db(
            """select code_id from t_codes where code_type = 'member_fee' and code_name = %s""", apply_member_type)
        member_fee = int(res['code_id'])
        form_args = {
            'form_id': form_rel_args['form_id'],
            'form_code': generate_uunum(),
            'apply_date': get_now_str(),
            'form_status': 'submitted',
            'update_date': get_now_str(),
            'apply_member_type': apply_member_type,
            'paid_money': member_fee,
            'form_notes': ''
        }
        form_res = yield self.insert_db_by_obj('t_form', form_args)
        yield send_email_to_manager(self, form_args['form_id'], 'person_first_instance')
        yield self.restful({"page": "/page/form_submitted"})


@Route(r"/page/(normal_member|advanced_member)")
class _(MgrHandler):
    @coroutine
    def post(self, entry):
        apply_member_type = entry
        person_args = self.get_args({
            'auth_id': '',
            'open_id': '',
            'fullname': '*',
            'gender': '*',
            'cellphone': '*',
            'email': '*',
            'address': '*',
            'school': '*',
            'school_start': '*',
            'education': '*',
            'person_info': '*',
            'birthday': '*',
            'city': '*',
            'wechatid': '*',
            'position': '*',
            'expects': '*',
            'wills': '*',
            'attachment': '',
            'school_number': '',
            'school_department': '',
            'first_normal_recommend': '',
            'second_normal_recommend': '',
            'first_advanced_recommend': '',
            'type': '',
            'weixin_group': '*'

        })
        # phone_code = self.get_argument("phonecode","")
        # if phone_code != self.get_cache("phone-bind-"+person_args['cellphone']) and phone_code != settings['session_secret']:
        #     yield self.error("验证码错误，请检查重试")
        #     return
        if not person_args:
            yield self.error('miss_param')
            return

        org_args = self.get_args({
            'org_name': '*',
            'general_description': '*',
            'domain_description': '*',
            'website': '',
            'industry': '*',
            'office_address': '',
            'high_tech': '',
            'comments': ''
        })

        if not org_args:
            yield self.error('miss_param')
            return

        # 如果t_title已存在相关职位,则取出title_id插入t_org_person,如果未存在则在t_title创建记录,再插入t_org_person
        title_id = ''
        res_title_name = yield self.query_db("select * from t_title where title_name = '{title_name}'".format(
            title_name=person_args['position']))
        if not res_title_name:
            res_id = yield self.query_db("select max(title_id)+1 as max_id from t_title")
            max_id = res_id[0]['max_id']
            yield self.insert_db(
                "insert into t_title (title_id,title_name) value ('{title_id}','{title_name}')".format(
                    title_id=max_id, title_name=person_args['position']))
            title_id = str(max_id)
        else:
            title_id = res_title_name[0]['title_id']

        # 如果申请人手机号 or 邮箱相同,则可以判断为同一个人
        person_info = yield self.fetchone_db(
            "select * from t_person where cellphone='{cellphone}' or email='{email}'".format(
                cellphone=person_args['cellphone'], email=person_args['email']))

        # 如果在t_person里面有记录
        if person_info:
            person_args['person_id'] = person_info['person_id']
            person_res = yield self.update_db_by_obj('t_person', person_args,
                                                     "person_id='%s'" % person_args['person_id'])
            f_form_info = yield self.fetchone_db(
                """select fr.form_id,f.form_id as f_form_id from t_form_relation as fr
                   left join t_form as f
                   on f.form_id = fr.form_id
                   where f.apply_member_type = '{apply_member_type}' and person_id = '{person_id}'""".format(
                    apply_member_type=apply_member_type, person_id=person_args['person_id']))
            if f_form_info and f_form_info['f_form_id']:
                logging.info('Reapply for %s' % apply_member_type)
                org_res = yield self.fetchone_db("select org_id from t_org where org_name = %s",
                                                 org_args['org_name'])
                if not org_res:
                    org_args['org_id'] = generate_uuid()
                    yield self.insert_db_by_obj('t_org', org_args)
                    org_person_args = {
                        'person_id': person_args['person_id'],
                        'org_id': org_args['org_id'],
                        'is_primary': 0,
                        'title_id': int(title_id)
                    }
                    t_form_args = {
                        'form_id': f_form_info['form_id'],
                        'update_date': get_now_str()
                    }
                    yield self.insert_db_by_obj('t_org_person', org_person_args)
                    yield self.update_db_by_obj('t_form', t_form_args, "form_id='%s'" % t_form_args['form_id'])
                else:
                    org_person = yield self.fetchone_db(
                        "select * from t_org_person where org_id = %s and person_id = %s",
                        org_res['org_id'], person_args['person_id'])
                    org_args['org_id'] = org_res['org_id']
                    org_person_args = {
                        'person_id': person_args['person_id'],
                        'org_id': org_args['org_id'],
                        'is_primary': 0,
                        'title_id': int(title_id)
                    }
                    t_form_args = {
                        'form_id': f_form_info['form_id'],
                        'update_date': get_now_str()
                    }
                    if not org_person:
                        yield self.insert_db_by_obj('t_org_person', org_person_args)
                    else:
                        yield self.update_db(
                            """update t_org_person set title_id = %d where person_id='%s' and org_id='%s'""" % (
                                int(title_id), person_args['person_id'], org_args['org_id']))
                    yield self.update_db_by_obj('t_form', t_form_args, "form_id='%s'" % t_form_args['form_id'])
                    yield self.update_db_by_obj('t_org', org_args, "org_id='%s'" % org_args['org_id'])
                    self.restful({"page": "/page/form_submitted"})
                    return
        else:
            person_args['person_id'] = generate_uuid()
            person_args['weixin_created'] = get_now_str()
            person_res = yield self.insert_db_by_obj('t_person', person_args)
        org_person = yield self.query_db("select * from t_org_person where person_id=%s ", person_args['person_id'])
        if org_person:
            org_args['org_id'] = org_person[0]['org_id']
            yield self.update_db_by_obj('t_org', org_args, "org_id='%s'" % org_args['org_id'])
        else:
            org_args['org_id'] = generate_uuid()
            org_res = yield self.insert_db_by_obj('t_org', org_args)
            org_person_args = {
                'person_id': person_args['person_id'],
                'org_id': org_args['org_id'],
                'is_primary': 0,
                'title_id': int(title_id)
            }
            person_org_res = yield self.insert_db_by_obj('t_org_person', org_person_args)
        form_rel_args = {
            'form_id': generate_uuid(),
            'person_id': person_args['person_id'],
            'org_id': ''
        }
        form_rel_res = yield self.insert_db_by_obj('t_form_relation', form_rel_args)
        # 预设会员费
        res = yield self.fetchone_db(
            """select code_id from t_codes where code_type = 'member_fee' and code_name = %s""", apply_member_type)
        member_fee = int(res['code_id'])
        form_args = {
            'form_id': form_rel_args['form_id'],
            'form_code': generate_uunum(),
            'apply_date': get_now_str(),
            'form_status': 'submitted',
            'update_date': get_now_str(),
            'apply_member_type': apply_member_type,
            'paid_money': member_fee,
            'form_notes': ''
        }
        form_res = yield self.insert_db_by_obj('t_form', form_args)
        yield send_email_to_manager(self, form_args['form_id'], 'person_first_instance')
        yield self.restful({"page": "/page/form_submitted"})


@Route(r"/page/(normal_org_member|advanced_org_member)")
class _(MgrHandler):
    @coroutine
    def post(self, entry):
        apply_member_type = entry
        FIRST_APPLY = True
        org_args = self.get_args({
            'org_name': '*',
            'general_description': '*',
            'domain_description': '*',
            'website': '',
            'industry': '*',
            'office_address': '',
            'representative': '*',
            'attachment': '',
            'high_tech': '',
            'comments': '',
            'type': ''
        })
        if not org_args:
            yield self.error('miss_param')
            return

        form_args = {
            'apply_date': get_now_str(),
            'form_status': 'submitted',
            'update_date': get_now_str(),
            'apply_member_type': apply_member_type,
            'form_notes': ''
        }
        counts = self.get_argument("counts")
        for i in range(0, int(counts)):
            person_args = self.get_args({
                'fullname%s' % i: '*',
                'gender%s' % i: '*',
                'cellphone%s' % i: '*',
                'email%s' % i: '*',
                'address%s' % i: '*',
                'school%s' % i: '*',
                'school_start%s' % i: '*',
                'school_number%s' % i: '',
                'education%s' % i: '*',
                'person_info%s' % i: '*',
                'birthday%s' % i: '*',
                'city%s' % i: '*',
                'wechatid%s' % i: '*',
                'position%s' % i: '*',
                'weixin_group%s' % i: '*',
                'expects': '*',
                'wills': '*',
                'first_normal_recommend': '',
                'second_normal_recommend': '',
                'first_advanced_recommend': '',
                'auth_id': '',
                'open_id': ''
            })

            # 如果申请人手机号 or 邮箱相同,则可以判断为同一个人
            person_info = yield self.fetchone_db(
                "select * from t_person where cellphone='{cellphone}' or email='{email}'".format(
                    cellphone=person_args['cellphone%s' % i], email=person_args['email%s' % i]))

            person = {
                'fullname': person_args['fullname%s' % i],
                'gender': person_args['gender%s' % i],
                'cellphone': person_args['cellphone%s' % i],
                'email': person_args['email%s' % i],
                'address': person_args['address%s' % i],
                'school': person_args['school%s' % i],
                'school_start': person_args['school_start%s' % i],
                'school_number': person_args['school_number%s' % i],
                'education': person_args['education%s' % i],
                'person_info': person_args['person_info%s' % i],
                'birthday': person_args['birthday%s' % i],
                'city': person_args['city%s' % i],
                'wechatid': person_args['wechatid%s' % i],
                'position': person_args['position%s' % i],
                'weixin_group': person_args['weixin_group%s' % i],
                'expects': person_args['expects'],
                'wills': person_args['wills'],
                'first_normal_recommend': person_args['first_normal_recommend'],
                'second_normal_recommend': person_args['second_normal_recommend'],
                'first_advanced_recommend': person_args['first_advanced_recommend'],
                'type': '',
                'person_id': '',
                'auth_id': '',
                'open_id': ''
            }
            # 如果t_title已存在相关职位,则取出title_id插入t_org_person,如果未存在则在t_title创建记录,再插入t_org_person
            title_id = ''
            res_title_name = yield self.fetchone_db("select * from t_title where title_name = '{title_name}'".format(
                title_name=person['position']))
            if not res_title_name:
                res_id = yield self.fetchone_db("select max(title_id)+1 as max_id from t_title")
                max_id = res_id['max_id']
                yield self.insert_db(
                    "insert into t_title (title_id,title_name) value ('{title_id}','{title_name}')".format(
                        title_id=max_id, title_name=person['position']))
                title_id = str(max_id)
            else:
                title_id = res_title_name['title_id']

            # 如果在t_person里面有记录
            if person_info:
                person_args['person_id'] = person_info['person_id']
                person_res = yield self.update_db_by_obj('t_person', person,
                                                         "person_id='%s'" % person['person_id'])
                f_form_info = yield self.fetchone_db(
                    """select op.org_id,fr.form_id,f.form_id as f_form_id from t_form_relation as fr
                       left join t_form as f
                       on fr.form_id = f.form_id
                       left join t_org_person as op
                       on fr.org_id = op.org_id and op.is_primary = 1
                       where  op.person_id = '{person_id}'
                       and f.apply_member_type = '{apply_member_type}'""".format(
                        apply_member_type=apply_member_type, person_id=person['person_id']))
                # 如果已经申请过企业会员
                if f_form_info and f_form_info['org_id'] and f_form_info['form_id'] and f_form_info['f_form_id']:
                    FIRST_APPLY = False
                    logging.info('Reapply for %s' % apply_member_type)
                    org_res = yield self.fetchone_db("select org_id from t_org where org_name = %s",
                                                     org_args['org_name'])
                    if not org_res:
                        org_args['org_id'] = generate_uuid()
                        yield self.insert_db_by_obj('t_org', org_args, "org_id=%s" % org_args['org_id'])
                        org_person_args = {
                            'person_id': person_args['person_id'],
                            'org_id': org_args['org_id'],
                            'is_primary': 1,
                            'title_id': int(title_id)
                        }
                        t_form_args = {
                            'form_id': f_form_info['form_id'],
                            'update_date': get_now_str()
                        }
                        yield self.insert_db_by_obj('t_org_person', org_person_args)
                        yield self.update_db_by_obj('t_form', t_form_args, "form_id='%s'" % t_form_args['form_id'])
                    else:
                        org_person = yield self.fetchone_db(
                            "select * from t_org_person where org_id = %s and person_id = %s",
                            org_res['org_id'], person_args['person_id'])
                        org_args['org_id'] = org_res['org_id']
                        org_person_args = {
                            'person_id': person_args['person_id'],
                            'org_id': org_args['org_id'],
                            'is_primary': 1,
                            'title_id': int(title_id)
                        }
                        t_form_args = {
                            'form_id': f_form_info['form_id'],
                            'update_date': get_now_str()
                        }
                        if not org_person:
                            yield self.insert_db_by_obj('t_org_person', org_person_args)
                        else:
                            yield self.update_db(
                                """update t_org_person set title_id = %d where person_id='%s' and org_id='%s'""" % (
                                int(title_id), person_args['person_id'], org_args['org_id']))
                        yield self.update_db_by_obj('t_form', t_form_args, "form_id='%s'" % t_form_args['form_id'])
                        yield self.update_db_by_obj('t_org', org_args, "org_id='%s'" % org_args['org_id'])
                        self.restful({"page": "/page/form_submitted"})
                        return
                else:
                    FIRST_APPLY = True
            else:
                person['person_id'] = generate_uuid()
                person_res = yield self.insert_db_by_obj('t_person', person)
            if FIRST_APPLY:
                org_res = yield self.fetchone_db("select * from t_org where org_name = %s ", org_args['org_name'])
                if org_res:
                    org_args['org_id'] = org_res['org_id']
                    yield self.update_db_by_obj('t_org', org_args, "org_id='%s'" % org_args['org_id'])
                else:
                    org_args['org_id'] = generate_uuid()
                    org_res = yield self.insert_db_by_obj('t_org', org_args)
                org_person_args = {
                    'person_id': person['person_id'],
                    'org_id': org_args['org_id'],
                    'is_primary': 1,
                    'title_id': int(title_id)
                }
                try:
                    person_org_res = yield self.insert_db_by_obj('t_org_person', org_person_args)
                except:
                    pass
        if FIRST_APPLY:
            org_res = yield self.fetchone_db("select * from t_org where org_name = %s ", org_args['org_name'])
            if org_res:
                org_args['org_id'] = org_res['org_id']
                yield self.update_db_by_obj('t_org', org_args, "org_id='%s'" % org_args['org_id'])
            else:
                org_args['org_id'] = generate_uuid()
            form_rel_args = {
                'form_id': generate_uuid(),
                'person_id': '',
                'org_id': org_args['org_id']
            }
            form_rel_res = yield self.insert_db_by_obj('t_form_relation', form_rel_args)
            # 预设会员费
            res = yield self.fetchone_db(
                """select code_id from t_codes where code_type = 'member_fee' and code_name = %s""", apply_member_type)
            member_fee = int(res['code_id'])
            form_args = {
                'form_id': form_rel_args['form_id'],
                'form_code': generate_uunum(),
                'apply_date': get_now_str(),
                'form_status': 'submitted',
                'update_date': get_now_str(),
                'apply_member_type': apply_member_type,
                'paid_money': member_fee,
                'form_notes': ''
            }
            form_res = yield self.insert_db_by_obj('t_form', form_args)
            yield send_email_to_manager(self, form_args['form_id'], 'org_first_instance')
        yield self.restful({"page": "/page/form_submitted"})


@Route(r"/page/(.*)")
class CommonMainPage(BasePage):
    @preassert_user
    @coroutine
    def get(self, entry='home'):
        page = get_page_by_entry(entry)
        navs = yield auth.get_mgr_navs(self)
        ctx = None
        if entry == 'form_weixin' or entry == 'form_normal' or entry == 'form_advanced' or entry == 'org_form_normal' or entry == 'org_form_advanced':
            ctx = yield self.query_db("select * from t_tag where tag_type='weixin_group'")
        elif entry == 'form_requirement':
            if not (self.is_member() and self.is_auth()):
                self.redirect("/page/requirement_unauth")

            ctx = yield self.query_db("select tag_id,tag_name from t_tag where tag_type='requirement_type'")
        self.render(page['layout'],
                    entry=entry,
                    page=page,
                    navs=navs,
                    page_config=map_config,
                    context=ctx)


@Route(r"/rest/page/form_normal")
class CommonMainPage_form_normal(BasePage):
    @preassert_user
    @coroutine
    def post(self):
        city_name = self.get_argument('city').encode('utf-8')
        school_name = self.get_argument('school').encode('utf-8')
        school_department_name = self.get_argument('school_department').encode('utf-8')
        position_name = self.get_argument('position').encode('utf-8')
        org_name = self.get_argument('org').encode('utf-8')
        industry_name = self.get_argument('industry').encode('utf-8')

        cities = []
        schools = []
        school_departments = []
        orgs = []
        industries = []
        titles = []

        city = yield self.query_db(
            "select district_name from dict_district where district_name like '%%{}%%'".format(city_name))
        school = yield self.query_db("select school from t_person where school like '%%{}%%'".format(school_name))
        school_department = yield self.query_db(
            "select school_department from t_person where school_department like '%%{}%%'".format(
                school_department_name))
        title = yield self.query_db(
            "select title_name from t_title where title_name like '%%{}%%'".format(position_name))
        org = yield self.query_db("select org_name from t_org where org_name like '%%{}%%'".format(org_name))
        industry = yield self.query_db("select industry from t_org where industry like '%%{}%%'".format(industry_name))
        for i in school:
            school = i['school'].rstrip()
            if school not in schools:
                schools.append(school)
        for i in title:
            title = i['title_name'].rstrip()
            if title not in titles:
                titles.append(title)
        for i in city:
            city = i['district_name'].rstrip()
            if city not in cities:
                cities.append(city)
        for i in school_department:
            school_department = i['school_department'].rstrip()
            if school_department not in school_departments:
                school_departments.append(school_department)
        for i in org:
            org = i['org_name'].rstrip()
            if org not in orgs:
                orgs.append(org)
        for i in industry:
            industry = i['industry'].rstrip()
            if industry not in industries:
                industries.append(industry)
        school_departments.sort()
        cities.sort()
        schools.sort()
        titles.sort()
        orgs.sort()
        industries.sort()
        self.write({
            'city': cities,
            'school': schools,
            'school_department': school_departments,
            'position': titles,
            'org': orgs,
            'industry': industries
        })


@Route(r"/console")
@Route(r"/console/")
class _(BasePage):
    @assert_user
    @assert_mgr
    @coroutine
    def get(self, entry='console'):
        self.redirect('/console/console')


@Route(r"/console/(survey_result)")
class MgrMainPage(BasePage):
    @assert_user
    @coroutine
    def get(self, entry):
        id = self.get_argument('id')
        user = self.current_user_profile
        navs = yield auth.get_mgr_navs(self)
        ctx = {}
        entry = "mgr_" + entry
        page = get_mgr_page_by_entry(entry, user)

        survey = yield get_survey(self, id, with_submits=True)
        ctx['survey'] = survey

        self.render("layout_console.html",
                    user=user,
                    entry=entry,
                    page=page,
                    navs=navs,
                    page_config=map_config,
                    context=ctx)


@Route(r"/console/(.*)")
class MgrMainPage(BasePage):
    @assert_mgr
    @coroutine
    def get(self, entry='console'):
        user = self.current_user_profile
        navs = yield auth.get_mgr_navs(self)
        entry = entry or 'console'
        ctx = {}
        if entry == 'console':
            if is_role_in(user['roles'], ['eventmgr_ygzx']) and not is_role_in(user['roles'], ['admin']):
                ctx['roles'] = 'eventmgr_ygzx'
                res = yield self.fetchone_db("""select group_concat(op.person_id  separator ''',''') as person_ids from t_auth_role as ar left join t_org_person as op on ar.person_id = op.person_id
                                                left join t_org as o on op.org_id = o.org_id 
                                                where ar.role_id = 'eventmgr_ygzx' and op.org_id = %s
                                                group by op.org_id""", user['org']['org_id'])
                person_ids = res['person_ids']
                print("kaibo: %s" % ','.join(person_ids))
                ctx['events_count'] = yield self.fetchone_db(
                    "select count(a.id) as count from t_news as a where status = 'published' and person_id in ('%s')" % person_ids)

                ctx['latest_events'] = yield self.query_db("""select id, title, pictures, published, 
                                                                activity_start_time, activity_end_time,
                                                                activity_sponsor,activity_undertake,activity_place,general_place,
                                                                DATE_FORMAT(activity_start_time, '%%Y年%%m月%%d日') as activity_start_date,
                                                                DATE_FORMAT(activity_end_time, '%%Y年%%m月%%d日') as activity_end_date,
                                                                DATE_FORMAT(activity_start_time, '%%H:%%i') as activity_start_hm,
                                                                DATE_FORMAT(activity_end_time, '%%H:%%i') as activity_end_hm,activity_online_offline
                                                                from 
                                                                t_news where status = 'published' and person_id in ('""" + person_ids + """') order by activity_start_time DESC limit 0, 3""")
            else:
                ctx['roles'] = user['roles']
                ctx['person_member_count'] = yield self.fetchone_db("select count(member_id) as count from t_member ")
                ctx['org_member_count'] = yield self.fetchone_db("""select count(a.member_id) as count from t_member as a,
                                                                    t_org_person as b
                                                                    where (a.member_type = 'advanced_org_member' or a.member_type = 'normal_org_member') and b.is_primary = 1 and a.org_id = b.org_id """)
                ctx['authorized_user_count'] = yield self.fetchone_db("""select count(a.person_id) as count
                                                                    from 
                                                                    t_person as a  """)
                ctx['wechat_member_count'] = yield self.fetchone_db("""select count(p.person_id) as count 
                                                                    from 
                                                                    t_person as p, t_org as o ,t_org_person as op 
                                                                    where p.type='weixin' and op.person_id = p.person_id and op.org_id = o.org_id """)
                ctx['articles_count'] = yield self.fetchone_db("""select count(a.id) as count 
                                                                    from 
                                                                    t_article as a where status = 'published'""")
                ctx['events_count'] = yield self.fetchone_db("""select count(a.id) as count 
                                                                    from 
                                                                    t_news as a where status = 'published'""")
                ctx['latest_articles'] = yield self.query_db("""select id, title,pictures, published
                                                                    from 
                                                                    t_article where status = 'published' order by published DESC limit 0, 3""")

                ctx['latest_events'] = yield self.query_db("""select id, title, pictures, published, 
                                                                    activity_start_time, activity_end_time,
                                                                    activity_sponsor,activity_undertake,activity_place,general_place,
                                                                    DATE_FORMAT(activity_start_time, '%%Y年%%m月%%d日') as activity_start_date,
                                                                    DATE_FORMAT(activity_end_time, '%%Y年%%m月%%d日') as activity_end_date,
                                                                    DATE_FORMAT(activity_start_time, '%%H:%%i') as activity_start_hm,
                                                                    DATE_FORMAT(activity_end_time, '%%H:%%i') as activity_end_hm,activity_online_offline
                                                                    from 
                                                                    t_news where status = 'published' order by activity_start_time DESC limit 0, 3""")
                ctx['latest_authorized_users'] = yield self.query_db("""select nick_name, head_img_url, auth_date
                                                                    from 
                                                                    t_person order by auth_date DESC limit 0, 8""")

        elif entry == 'article_new':
            ctx['article_sources'] = yield self.query_db(
                "select * from t_tag where tag_type = 'article_source' order by tag_sort ASC, tag_name ASC ")

        elif entry == 'dataset_new':
            ctx['dataset_type'] = yield self.query_db(
                "select * from t_tag where tag_type = 'dataset_type' order by tag_sort ASC, tag_name ASC ")

        elif entry == 'requirement_new':
            ctx['article_sources'] = yield self.query_db(
                "select * from t_tag where tag_type = 'requirement_type' order by tag_sort ASC, tag_name ASC ")

        elif entry == 'sign_up_list' or entry == 'register_list':
            activity_id = self.get_argument("activity", "")
            ctx = yield self.query_db("select title, id from t_news where id=%s", activity_id)

        elif entry == 'discussion_sign_up_list':
            activity_id = self.get_argument("activity", "")
            ctx = yield self.query_db("select title, id from t_discussion where id=%s", activity_id)


        elif entry == 'merge_org_list' or entry == 'role_list' or entry == 'group_tree' or entry=='manager_list' or entry=='form_list' or entry=='org_form_list' or entry=='weixin_apply_list' or entry=='member_person_list' or entry=='member_org_list'  or entry=='channel_list' or entry=='discussion_list':
            ctx['roles'] = ""
            for item in user['roles']:
                ctx['roles'] = "%s%s," % (ctx['roles'], item['role_id'])
            ctx['auth_id'] = user['authorized']['auth_id']
            ctx['person_id'] = self.current_user
            ctx['form_status'] = yield self.query_db(
                "select code_id , code_name from t_codes where code_type='form_status' and code_id!='paid'")
            ctx['mgr_roles'] = yield self.query_db(
                "select code_id as role_id, code_name as role_name from t_codes where code_type='mgr_role' order by code_sort")
            if entry == 'role_list':
                ctx['mgr_pages'] = get_all_mgr_pages()

        elif entry == 'edit_member_info':
            person_id = self.get_argument('person_id', '')
            org_id = self.get_argument('org_id', '')
            ctx = {}
            if person_id:
                ctx['type'] = 'person'
                ctx['member'] = yield self.fetchone_db(
                    "SELECT m.*,c.code_name as member_type_name FROM t_member m left join t_form_relation fr on m.form_id = fr.form_id left join t_codes as c on m.member_type=c.code_id where c.code_type='member_type' and fr.person_id =%s",
                    person_id)
            if org_id:
                ctx['type'] = 'org'
                ctx['member'] = yield self.fetchone_db(
                    "SELECT m.*,c.code_name as member_type_name FROM t_member m left join t_form_relation fr on m.form_id = fr.form_id left join t_codes as c on m.member_type=c.code_id where c.code_type='member_type' and fr.org_id =%s",
                    org_id)
            ctx['status'] = yield self.query_db(
                "select code_name , code_id from t_codes where code_type='member_status'")

        elif entry == 'merge_org_info':
            person_id = self.get_argument('person_id', '')
            org_id = self.get_argument('org_id', '')
            ctx = {}
            if person_id:
                ctx['type'] = 'person'
                ctx['member'] = yield self.fetchone_db(
                    "SELECT m.*,c.code_name as member_type_name FROM t_member m left join t_form_relation fr on m.form_id = fr.form_id left join t_codes as c on m.member_type=c.code_id where c.code_type='member_type' and fr.person_id =%s",
                    person_id)
            if org_id:
                ctx['type'] = 'org'
                ctx['member'] = yield self.fetchone_db(
                    "SELECT m.*,c.code_name as member_type_name FROM t_member m left join t_form_relation fr on m.form_id = fr.form_id left join t_codes as c on m.member_type=c.code_id where c.code_type='member_type' and fr.org_id =%s",
                    org_id)
            ctx['status'] = yield self.query_db(
                "select code_name , code_id from t_codes where code_type='member_status'")


        elif entry == 'activity_new':
            if is_role_in(user['roles'], ['eventmgr_ygzx']) and not is_role_in(user['roles'], ['admin']):
                ctx['roles'] = 'eventmgr_ygzx'
                res = yield self.fetchone_db("""select group_concat(op.person_id separator ''',''') as person_ids from t_auth_role as ar left join t_org_person as op on ar.person_id = op.person_id
                                                left join t_org as o on op.org_id = o.org_id 
                                                where ar.role_id = 'eventmgr_ygzx' and op.org_id = %s
                                                group by op.org_id""", user['org']['org_id'])
                person_ids = res['person_ids']
                id = self.get_argument("id", '')
                if id != '':
                    sql = ("""
                    select title,subject,left(published,10) as published, content , 
                            data_source, data_type, pictures ,activity_start_time,
                            activity_end_time,activity_undertake,activity_sponsor,
                            activity_place,activity_type,activity_online_offline,
                            paid,sign_up_check,general_place,signup_content,sign_up_fields,
                            a.sur_id,b.sur_title,activity_organizer,activity_support,activity_cooperate,channel_fields,event_corp_auth
                            from t_news as a LEFT JOIN t_survey as b on b.sur_id = a.sur_id where id = """+id+""" and a.person_id in ('"""+person_ids+"""') 
                    """)
                    result = yield self.fetchone_db(sql)
                    if len(result) == 0:
                        yield self.redirect('/console/unauth')

        entry = "mgr_" + entry
        page = get_mgr_page_by_entry(entry, user)
        self.render("layout_console.html",
                    user=user,
                    entry=entry,
                    page=page,
                    navs=navs,
                    page_config=map_config,
                    context=ctx)

@Route(r"/coderain")
class _(BasePage):
    @assert_user
    @coroutine
    def get(self, entry="coderain"):
        page = get_page_by_entry(entry)

        self.render(page['layout'],
                    entry=entry,
                    page=page,
                    page_config=map_config,
                    context=None)


def get_console_page_routes():
    return [('/(' + '|'.join([x['id'] for x in BODY_PAGES]) + ')', ConsoleMainPage)] + [
        ('/(' + '|'.join([x['id'] for x in COMMON_PAGES]) + ')', CommonMainPage)]


def get_mgr_page_routes():
    return [('/(' + '|'.join([x['id'] for x in MGR_PAGES]) + ')', MgrMainPage)] + [
        ('/(' + '|'.join([x['id'] for x in COMMON_PAGES]) + ')', CommonMainPage)]


@Route(r"/old_msie")
class OldMSIE(BasePage):
    def get(self):
        self.render("msie.html")


class NotFoundPage(BasePage):
    @tornado.gen.coroutine
    def get(self, entry):
        if not entry:
            self.redirect('/')
        if self.request.uri.find('rest/') >= 0:
            yield self.response_error('access_not_exist', status_code='404')
        else:
            self.redirect('/404?page=' + entry)


# 日志查看
@Route(r"/logs/view/#bottom")
@Route(r"/logs/view")
class _(BasePage):
    @coroutine
    def get(self):
        entry = 'logs_view'
        file_path = '//var/log/supervisord/marsweb_error.log'
        with open(file_path, 'rb') as fp:
            file_size = getsize(file_path)
            read_size = file_size - 1024 * 500
            fp.seek(read_size)
            last_pos = fp.tell()
            a = fp.readlines(1024 * 500)
            ctx = dict()
            page = get_page_by_entry(entry)
            ctx['logs'] = a
        self.render(page['layout'],
                    entry=entry,
                    page=page,
                    page_config=map_config,
                    context=ctx)


@Route(r"/rest/logs/view")
class _(BasePage):
    @coroutine
    def get(self):
        file_path = ''
        file_name = self.get_argument("file_name", "")
        if file_name and 'web' in file_name:
            file_path = '//var/log/supervisord/marsweb_error.log'
        else:
            file_path = '//var/log/mysql/' + file_name + '.log'
        with open(file_path, 'rb') as fp:
            file_size = getsize(file_path)
            read_size = file_size - 1024 * 50
            fp.seek(read_size)
            last_pos = fp.tell()
            a = fp.readlines(1024 * 50)
        yield self.restful({
            'logs': a
        })
