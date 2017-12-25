# -*- coding: utf-8 -*-  

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
from lib.treelib import Tree, Node


@coroutine
def check_vote_result(handler):
    '''
    检查为期7天的会员申请投票结果
    投票成功后三个月未缴费的处理
    :param handler:
    :return:
    '''
    d1 = datetime.datetime.today()
    d2 = d1 + datetime.timedelta(-7)
    preDay = d2.strftime('%Y-%m-%d %H:%M:%S')
    form_list = yield handler.query_db("select * from t_form where form_status='voting' and vote_start_time <= %s",
                                       preDay)
    for item in form_list:
        type = item['apply_member_type']
        form_id = item['form_id']
        person_info = yield handler.fetchone_db("""select p.cellphone from t_form as f , t_person as p ,
                t_form_relation as fr left join t_org_person as op on fr.org_id=op.org_id and op.is_primary=1 where f.form_id=fr.form_id and fr.person_id=p.person_id and f.form_id=%s""",
                                                form_id)
        try:
            if type == 'normal_member' or type == 'normal_org_member':
                number = yield handler.fetchone_db(
                    "select count(1) as total,sum(case attitue when 'agree' then 1 else 0 end) as agree ,sum(case attitue when 'oppose' then 1 else 0 end) as oppose,sum(case attitue when 'waive' then 1 else 0 end) as waive from t_vote_record where form_id=%s",
                    form_id)

                if number['agree'] * 2 < number['total']:
                    yield handler.update_db("update t_form set form_status='votedfailed' where form_id = %s", form_id)
                    yield send_message(person_info['cellphone'], handler.config['not_pass_vote'], handler.config)
                else:
                    yield handler.update_db(
                        "update t_form set form_status='votedsuccess' , vote_success_time=%s where form_id = %s",
                        get_now_str(),
                        form_id)
                    yield send_email_to_manager(handler, form_id, 'charge')
                    yield send_message(person_info['cellphone'], handler.config['pass_vote'], handler.config)

            else:
                number = yield handler.fetchone_db(
                    "select count(1) as total,sum(case attitue when 'agree' then 1 else 0 end) as agree ,sum(case attitue when 'oppose' then 1 else 0 end) as oppose,sum(case attitue when 'waive' then 1 else 0 end) as waive from t_vote_record where form_id=%s",
                    form_id)
                if number['agree'] and number['total'] and number['agree'] * 2 >= number['total']:
                    yield handler.update_db(
                        "update t_form set form_status='votedsuccess', vote_success_time=%s where form_id = %s",
                        get_now_str(),
                        form_id)
                    yield send_email_to_manager(handler, form_id, 'charge')
                    yield send_message(person_info['cellphone'], handler.config['pass_vote'], handler.config)
                else:
                    yield handler.update_db("update t_form set form_status='votedfailed' where form_id = %s", form_id)
        except Exception as e:
            logging.info('error:%s,form_id:%s' % (e, form_id))

    d3 = d1 + datetime.timedelta(-83)
    day3 = d3.strftime('%Y-%m-%d')
    remind_form_list = yield handler.query_db(
        "select * from t_form where form_status='votedsuccess' and left(vote_success_time,10) = %s", day3)
    for item in remind_form_list:
        form_id = item['form_id']
        person_info = yield handler.fetchone_db("""select p.cellphone from t_form as f , t_person as p ,
                t_form_relation as fr left join t_org_person as op on fr.org_id=op.org_id and op.is_primary=1 where f.form_id=fr.form_id and fr.person_id=p.person_id and f.form_id=%s""",
                                                form_id)
        yield send_message(person_info['cellphone'], handler.config['remind_payment'], handler.config)

    d4 = d1 + datetime.timedelta(-90)
    day4 = d4.strftime('%Y-%m-%d')
    delete_form_list = yield handler.query_db(
        "select * from t_form where form_status='votedsuccess' and left(vote_success_time,10) = %s", day4)
    for item in delete_form_list:
        form_id = item['form_id']
        yield send_email_to_manager(handler, form_id, 'delete_apply')


@Route(r"/rest/check_expired_result")
class _(MgrHandler):
    '''
    过期会员检查
    '''

    @coroutine
    def get(self):
        self.check_expired_result()
        self.write({"message": 'Done!'})

    def check_expired_result(handler):
        d1 = datetime.datetime.today()
        d2 = d1 + datetime.timedelta(-7)
        preDay = d2.strftime('%Y-%m-%d %H:%M:%S')
        # form_list = yield handler.query_db("select * from t_member where due_date <= {preDay}".format(preDay=preDay))


@coroutine
def generate_person_org_html(handler, form_id):
    '''
    会员申请中,审批和审核完之后发邮件给管理员,这个函数制作html格式的邮件内容
    :param handler:
    :param form_id: 申请form的form_id
    :return:
    '''
    # 如果是企业会员申请,is_primary = 1 且在t_form_relation中只有org_id,而没有person_id
    res = yield handler.fetchone_db('''
        select f.form_code,f.apply_member_type,f.form_id,f.apply_date,f.form_status,
        c1.code_name as apply_member_type_name,o.*,
        p.*,c1.code_name as form_status_name from t_form_relation as fr
        inner join t_form as f
        on f.form_id = fr.form_id
        inner JOIN t_codes as c1
        ON c1.code_type = 'member_type' and c1.code_id = f.apply_member_type
        inner JOIN t_codes as c2
        ON c2.code_type = 'form_status' and c2.code_id = f.form_status,
        t_org_person as op
        inner join t_org as o
        on op.org_id = o.org_id
        inner JOIN t_person as p on
        p.person_id = op.person_id
        where f.form_status <> 'deleted'
        and op.is_primary = 1
	    and op.org_id = fr.org_id
        and f.form_id = %s
        ''', form_id)
    if not res:
        # 如果不是企业会员,则是个人会员申请,is_primary为0,且t_form_relation中只有person_id,而没有org_id
        res = yield handler.fetchone_db(
            '''
            select f.form_code,f.apply_member_type,f.form_id,f.apply_date,f.form_status,
            c1.code_name as apply_member_type_name,o.*,
            p.*,c1.code_name as form_status_name from t_form as f
            LEFT JOIN t_codes as c1
            ON c1.code_type = 'member_type' and c1.code_id = f.apply_member_type
            LEFT JOIN t_codes as c2
            ON c2.code_type = 'form_status' and c2.code_id = f.form_status,
            t_org as o, t_form_relation as fr,
            t_org_person as op
            LEFT JOIN t_person as p on
            p.person_id = op.person_id
            where f.form_status <> 'deleted'
            and fr.form_id = f.form_id
            and fr.person_id = p.person_id
            and op.is_primary = 0
            and op.org_id = o.org_id
            and f.form_id = %s
            ''', form_id)
    gender = str()
    if res and res['gender'] and res['gender'] == 1:
        gender = '男'
    elif res and res['gender'] and res['gender'] == 2:
        gender = '女'
    person_info = """
        <table>
            <tr>
                <h4>""" + res['fullname'] + """</h4>
                <td class="one">
                    性别
                </td>
                <td class="two">
                    """ + gender + """
                </td>
            </tr>
            <tr>
                <td class="one">
                    出生日期
                </td>
                <td class="two">
                    """ + str(res['birthday']) + """
                </td>
            </tr>
            <tr>
                <td class="one">
                    毕业院校
                </td>
                <td class="two">
                    """ + res['school'] + """
                </td>
            </tr>
            <tr>
                <td class="one">
                    入学年份
                </td>
                <td class="two">
                    """ + str(res['school_start']) + """
                </td>
            </tr>
            <tr>
                <td class="one">
                    学历
                </td>
                <td class="two">
                    """ + res['education'] + """
                </td>
            </tr>
            <tr>
                <td class="one">
                    手机号码
                </td>
                <td class="two">
                    """ + res['cellphone'] + """
                </td>
            </tr>
            <tr>
                <td class="one">
                    申请加入的微信群
                </td>
                <td class="two">
                    """ + res['weixin_group'] + """
                </td>
            </tr>
            <tr>
                <td class="one">
                    微信号
                </td>
                <td class="two">
                    """ + res['wechatid'] + """
                </td>
            </tr>
            <tr>
                <td class="one">
                    Email
                </td>
                <td class="two">
                    """ + res['email'] + """
                </td>
            </tr>
            <tr>
                <td class="one">
                    通讯地址
                </td>
                <td class="two">
                    """ + res['address'] + """
                </td>
            </tr>
            <tr>
                <td class="one">
                    个人背景简介
                </td>
                <td class="two">
                    """ + res['person_info'] + """
                </td>
            </tr>
            <tr>
                <td class="one">
                    推荐人1
                </td>
                <td class="two">
                    """ + str(res['first_normal_recommend']) + """
                </td>
            </tr>
            <tr>
                <td class="one">
                    推荐人2
                </td>
                <td class="two">
                    """ + str(res['second_normal_recommend']) + """
                </td>
            </tr>
            <tr>
                <td class="one">
                    推荐人3
                </td>
                <td class="two">
                    """ + str(res['first_advanced_recommend']) + """
                </td>
            </tr>
            <tr>
                <td class="one">
                    希望获取的服务或者资源
                </td>
                <td class="two">
                    """ + str(res['expects']) + """
                </td>
            </tr>
            <tr>
                <td class="one">
                    可提供的资源或服务
                </td>
                <td class="two">
                    """ + str(res['wills']) + """
                </td>
            </tr>
        </table>
        """
    org_info = """
        <table class="twelve columns">
            <tr>
                <td>
                    <h4>""" + res['org_name'] + """</h4>
                    <table>
                        <tr>
                            <td class="one">
                                职位
                            </td>
                            <td class="two">
                                """ + res['position'] + """
                            </td>
                        </tr>
                        <tr>
                            <td class="one">
                                所属行业
                            </td>
                            <td class="two">
                                """ + res['industry'] + """
                            </td>
                        </tr>
                        <tr>
                            <td class="one">
                                公司简介
                            </td>
                            <td class="two">
                                """ + res['general_description'] + """
                            </td>
                        </tr>
                        <tr>
                            <td class="one">
                                业务范围
                            </td>
                            <td class="two">
                                """ + res['domain_description'] + """
                            </td>
                        </tr>
                        <tr>
                            <td class="one">
                                公司网址
                            </td>
                            <td class="two">
                                <a href=""" + res['website'] + """>""" + res['website'] + """</a>
                            </td>
                        </tr>
                    </table>
                </td>
                <td class="expander"></td>
            </tr>
        </table>
        """
    ctx = dict()
    ctx['person_info'] = person_info
    ctx['org_info'] = org_info
    # 会员类型中文名
    if res.has_key('apply_member_type_name'):
        ctx['apply_member_type_name'] = res['apply_member_type_name']
    # 会员类型英文名
    if res.has_key('apply_member_type'):
        ctx['apply_member_type'] = res['apply_member_type']
    ctx['fullname'] = res['fullname']
    ctx['org_name'] = res['org_name']
    raise Return(ctx)


@coroutine
def send_email_to_manager(handler, form_id, action):
    # 动作分别是个人申请,企业申请,投票,通知缴费,删除申请
    all_actions = ['person_first_instance', 'org_first_instance', 'vote', 'charge', 'delete_apply']
    if action not in all_actions:
        return
    if action == 'org_first_instance' or action == 'person_first_instance' or action == 'delete_apply':
        # 发邮件给会员管理员
        handle_person = yield handler.query_db(
            "select t.person_id, p.email , p.fullname from t_auth_role as t , t_person as p where t.role_id='operator' and t.person_id = p.person_id ")
        # logging.info("send_email_to_manager handle_person:%s" % handle_person)
        res = yield generate_person_org_html(handler, form_id)
        first_instance_reviewed_success = first_instance_reviewed_failed = failed_uuid = str()
        for item in handle_person:
            if action == 'delete_apply':
                first_instance_reviewed_success = "%s|%s|%s|delete_apply" % (action, form_id, item['person_id'])
                success_uuid = generate_uuid()
                failed_uuid = None
            elif action == 'person_first_instance' or action == 'org_first_instance':
                first_instance_reviewed_success = "%s|%s|%s|voting" % (action, form_id, item['person_id'])
                success_uuid = generate_uuid()
                first_instance_reviewed_failed = "%s|%s|%s|reviewed_failed" % (action, form_id, item['person_id'])
                failed_uuid = generate_uuid()

            handler.set_cache(success_uuid, first_instance_reviewed_success, 604800)
            if failed_uuid:
                handler.set_cache(failed_uuid, first_instance_reviewed_failed, 604800)
            if action == 'delete_apply':
                button_info = """<table class="row">
                                <tr>
                                    <td class="wrapper">
                                        <!-- begin four columns -->
                                        <table class="six columns">
                                            <table class="btn white">
                                                <tr>
                                                    <td>
                                                        <a href=""" + handler.config[
                    'site_host_url'] + 'rest/action?uuid=' + success_uuid + """>删除该申请</a>
                                                    </td>
                                                </tr>
                                            </table>
                                        </table>
                                    </td>
                                </tr>
                            </table>"""
            else:
                button_info = """<table class="row">
                                <tr>
                                    <td class="wrapper">
                                        <!-- begin four columns -->
                                        <table class="six columns">
                                            <table class="btn white">
                                                <tr>
                                                    <td>
                                                        <a href=""" + handler.config[
                    'site_host_url'] + 'rest/action?uuid=' + success_uuid + """>通过审核</a>
                                                    </td>
                                                </tr>
                                            </table>
                                        </table>
                                    </td>
                                    <td class="wrapper">
                                        <table class="six columns">
                                            <table class="btn red">
                                                <tr>
                                                    <td>
                                                        <a href=""" + handler.config[
                                  'site_host_url'] + 'rest/action?uuid=' + failed_uuid + """>退回</a>
                                                    </td>
                                                </tr>
                                            </table>
                                        </table>
                                        <!-- end four columns -->
                                    </td>
                                </tr>
                            </table>"""

            fr = open("tpl/test_email_newsletter.html", "r")
            content = fr.read()
            title = str()
            if action == 'person_first_instance' or action == 'org_first_instance':
                content = content.replace("main_title", u"申请成为%s,等待初审" % res['apply_member_type_name'])
                title = u'%s申请成为%s,等待初审' % (res['fullname'], res['apply_member_type_name'])
            elif action == 'delete_apply':
                content = content.replace("main_title", u"会员资格获得批准后，三个月内未缴纳会费")
                title = u'%s会员资格获得批准后，三个月内未缴纳会费' % (res['fullname'])
            else:
                content = content.replace("main_title", u"申请成为%s,等待审核" % res['apply_member_type_name'])
                title = u'%s申请成为%s,等待审核' % (res['fullname'], res['apply_member_type_name'])
            content = content.replace("person_info", res['person_info'])
            content = content.replace("org_info", res['org_info'])
            content = content.replace("check_info", u"审核是否通过该申请")
            content = content.replace("click_infos", button_info)
            try:
                send_email(title, item['email'], content, handler.config)
            except:
                pass

    elif action == 'vote':
        # 发邮件给秘书处管理员
        master_person = yield handler.query_db(
            "select t.person_id , p.email,p.fullname from t_auth_role as t , t_person as p  where t.role_id='master' and t.person_id = p.person_id ")
        res = yield generate_person_org_html(handler, form_id)

        advanced_member_list = yield handler.member_type_list(advanced=True, code_name=True)

        ###***以下注释代码是给理事会员发邮件进行投票,现在暂不需要,但先不要删除(by 鸿森)***##########
        # # 先从数据库中查找所有的企业会员
        # org_member = yield handler.query_db("select code_name from t_codes where code_type='member_type' and code_id like '%%org%%'")
        # org_member_list = [m['code_name'] for m in org_member]
        # 如果申请的会员是理事会员
        # if res['apply_member_type_name'] in advanced_member_list:
        #     #查询所有企业理事会员
        #     advanced_org_member = yield handler.query_db(
        #         """select p.person_id,p.email,p.fullname from t_person as p
        #             left join t_org_person as op
        #             on op.person_id = p.person_id
        #             left join t_member as m
        #             on m.org_id = op.org_id
        #             where op.is_primary = 1 and m.status = 'valid'
        #             and m.member_type = 'advanced_org_member'""")
        #     for item in advanced_org_member:
        #         master_person.append(item)
        #     advanced_member = yield handler.query_db("""select p.person_id,p.email,p.fullname from t_person as p
        #                                                 left join t_member as m
        #                                                 on p.person_id = m.person_id
        #                                                 where m.member_type = 'advanced_member'
        #                                                 and m.status = 'valid'""")
        #     for item in advanced_member:
        #         master_person.append(item)
        for item in master_person:
            vote_agree = "%s|%s|%s|agree" % (action, form_id, item['person_id'])
            agree_uuid = generate_uuid()
            vote_oppose = "%s|%s|%s|oppose" % (action, form_id, item['person_id'])
            oppose_uuid = generate_uuid()
            vote_waive = "%s|%s|%s|waive" % (action, form_id, item['person_id'])
            waive_uuid = generate_uuid()
            handler.set_cache(agree_uuid, vote_agree, 604800)
            handler.set_cache(oppose_uuid, vote_oppose, 604800)
            handler.set_cache(waive_uuid, vote_waive, 604800)
            button_info = """<table class="row">
                                <tr>
                                    <td class="wrapper">
                                        <table class="four columns">
                                            <table class="btn white">
                                                <tr>
                                                    <td>
                                                        <a href=""" + handler.config[
                'site_host_url'] + 'rest/action?uuid=' + agree_uuid + """>赞成加入</a>
                                                    </td>
                                                </tr>
                                            </table>
                                        </table>
                                    </td>
                                    <td class="wrapper">
                                        <table class="four columns">
                                            <table class="btn red">
                                                <tr>
                                                    <td>
                                                        <a href=""" + handler.config[
                              'site_host_url'] + 'rest/action?uuid=' + oppose_uuid + """>反对加入</a>
                                                    </td>
                                                </tr>
                                            </table>
                                        </table>
                                    </td>
                                    <td class="wrapper">
                                        <table class="four columns">
                                            <table class="btn blue">
                                                <tr>
                                                    <td>
                                                        <a href=""" + handler.config[
                              'site_host_url'] + 'rest/action?uuid=' + waive_uuid + """>弃权</a>
                                                    </td>
                                                </tr>
                                            </table>
                                        </table>
                                    </td>
                                </tr>
                            </table>"""
            fr = open("tpl/test_email_newsletter.html", "r")
            content = fr.read()
            content = content.replace("main_title", u"申请成为%s,请投票" % res['apply_member_type_name'])
            content = content.replace("person_info", res['person_info'])
            content = content.replace("org_info", res['org_info'])
            content = content.replace("check_info", u"会员申请公示及投票")
            content = content.replace("click_infos", button_info)

            if item['email'] and (res['apply_member_type_name'] in advanced_member_list):
                try:
                    logging.info("Send email to %s" % item['email'])
                    send_email(u'%s申请成为%s,请投票' % (res['fullname'], res['apply_member_type_name']), item['email'],
                               content,
                               handler.config)
                except:
                    logging.info("this email sent failed : %s" % item['email'])
            elif item['email']:
                try:
                    logging.info("Send email to %s" % item['email'])
                    send_email(u'%s申请成为%s,请投票' % (res['fullname'], res['apply_member_type_name']), item['email'],
                               content,
                               handler.config)
                except:
                    logging.info("this email sent failed : %s" % item['email'])

    elif action == 'charge':
        # 发邮件给会员管理员
        operator_person = yield handler.query_db(
            "select t.person_id , p.email ,p.fullname from t_auth_role as t , t_person as p where t.role_id='operator' and t.person_id = p.person_id")
        res = yield generate_person_org_html(handler, form_id)
        fr = open("tpl/test_email_newsletter.html", "r")
        content = fr.read()
        content = content.replace("main_title", u"申请成为%s已通过投票，请通知缴费" % res['apply_member_type_name'])
        content = content.replace("person_info", res['person_info'])
        content = content.replace("org_info", res['org_info'])
        content = content.replace("check_info", "")
        content = content.replace("click_infos", "")
        for item in operator_person:
            if item['email']:
                send_email(u'%s申请成为%s已通过投票，请通知缴费' % (res['fullname'], res['apply_member_type_name']), item['email'],
                           content, handler.config)


@Route(r"/mgr/rest/checkin/events")
class _(MgrHandler):
    @coroutine
    def get(self):
        res = yield self.query_db(
            "select id ,title,activity_start_time as start_time,activity_end_time as end_time,activity_place as place from t_news order by activity_start_time DESC")
        yield self.restful(res)


@Route(r"/mgr/rest/checkin/events/(.*)/qrlist")
class _(MgrHandler):
    @coroutine
    def get(self, activity_id):
        res = yield self.query_db("select id , id as name, created, concat('" + self.config[
            'site_host_url'] + "rest/qrcode?type=pure&link=', id) as qrcode from t_signup where event_id=%s ",
                                  activity_id)
        yield self.restful(res)


@Route(r"/mgr/rest/checkin/events/(.*)/qrlist/checkined")
class _(MgrHandler):
    @coroutine
    def post(self, activity_id):
        qrlist = json.loads(self.get_argument('qrlist', '') or self.request.body)
        res = None
        for q in qrlist:
            res = yield self.execute_db("update t_signup set checked_in = %s where event_id = %s and id = %s",
                                        q['datetime'], activity_id, q['id'])
        if res is not None:
            yield self.restful({"message": "上传成功"})
        else:
            yield self.error("上传失败")


@Route(r"/ticket/events/(.*)/qr/(.*)")
class _(MgrHandler):
    @coroutine
    def get(self, activity_id, user_id):
        res = yield self.fetchone_db(
            "select id ,title,activity_start_time as start_time,activity_end_time as end_time,activity_place as place from t_news where id = %s order by activity_start_time DESC",
            activity_id)
        res2 = yield self.fetchone_db("select id , name, created, concat('" + self.config[
            'site_host_url'] + "rest/qrcode?type=pure&link=', id) as qrcode from t_signup where event_id=%s and id = %s",
                                      activity_id, user_id)

        ctx = {
            'event': res,
            'user': res2
        }

        self.render("ext/signup_ticket.html",
                    context=ctx)


@Route(r"/mgr/rest/checkin/events/(.*)/qrlist/send_sms")
class _(MgrHandler):
    # @asynchronous
    @coroutine
    def get_short_url(self, url):
        # 获取accesstoken与openid
        client = tornado.httpclient.AsyncHTTPClient()
        accesstoken = self.get_cache('weixin-access_token')
        if not accesstoken:
            request = tornado.httpclient.HTTPRequest(
                url='https://api.weixin.qq.com/cgi-bin/token?' +
                    urllib.urlencode({"appid": self.config['wechat_appid'], "secret": self.config['wechat_secret'],
                                      "grant_type": "client_credential"}),
                method="GET",
                validate_cert=False
            )
            resp = yield client.fetch(request)
            body = json.loads(resp.body)
            accesstoken = body['access_token']
            self.set_cache('weixin-access_token', accesstoken, 60)

        request = tornado.httpclient.HTTPRequest(
            url="https://api.weixin.qq.com/cgi-bin/shorturl?" +
                urllib.urlencode({"access_token": accesstoken}),
            body=dump_json({"action": "long2short", "long_url": url}),
            method="POST",
            validate_cert=False
        )
        resp = yield client.fetch(request)
        body = json.loads(resp.body)
        short_url = body['short_url']
        raise Return(short_url)

    @coroutine
    # @assert_user #@assert_user(roles=['admin','operator','master'])
    def get(self, activity_id):
        event = yield self.fetchone_db("select * from t_news where id = %s", activity_id)
        res = yield self.query_db("select id, name, cellphone, created, '" + self.config[
            'site_host_url'] + "page/events/" + activity_id + "' as url from t_signup where event_id=%s and sms_content = '' ",
                                  activity_id)
        for i in res:
            cellphone = i['cellphone']
            if cellphone:
                code = cellphone.strip()
                # code = '18911631389'
                url = yield self.get_short_url(i['url'])
                msg = self.config['event_signup_sms'] % {'url': str(url), 'name': event.title,
                                                         'time': event.activity_start_time,
                                                         'place': event.activity_place}
                yield send_message(code, msg, self.config)
                yield self.update_db("update t_signup set sms_sent = now(), sms_content = %s where id = %s", msg,
                                     i['id'])
        yield self.restful({
            "message": "报名短信已发送到手机"
        })
        return


##之前为了某个活动取消,发短信和邮件通知报名用户而写的,以防再有相同事件，所以暂时不删除（by 鸿森）
# @Route(r"/mgr/rest/checkin/events/(.*)/qrlist/send_sms_email_event_cancel")
# class _(MgrHandler):
#     @coroutine
#     def send_cancel_mail(self, email):
#         if email:
#             title = u'【活动取消通知】工业大数据采集与分析-复旦大数据思享会'
#             content = self.config['event_cancel_msg']
#             self.config['noreply_mail_name'] = u'复旦大数据思享会'
#             try:
#                 yield send_email(title, email, content, self.config)
#             except Exception as e:
#                 logging.info(e)

# @asynchronous
# @coroutine
# def get_short_url(self, url):
#     # 获取accesstoken与openid
#     client = tornado.httpclient.AsyncHTTPClient()
#     accesstoken = self.get_cache('weixin-access_token')
#     if not accesstoken:
#         request = tornado.httpclient.HTTPRequest(
#             url='https://api.weixin.qq.com/cgi-bin/token?' +
#                 urllib.urlencode({"appid": self.config['wechat_appid'], "secret": self.config['wechat_secret'],
#                                   "grant_type": "client_credential"}),
#             method="GET",
#             validate_cert=False
#         )
#         resp = yield client.fetch(request)
#         body = json.loads(resp.body)
#         accesstoken = body['access_token']
#         self.set_cache('weixin-access_token', accesstoken, 60)
#
#     request = tornado.httpclient.HTTPRequest(
#         url="https://api.weixin.qq.com/cgi-bin/shorturl?" +
#             urllib.urlencode({"access_token": accesstoken}),
#         body=dump_json({"action": "long2short", "long_url": url}),
#         method="POST",
#         validate_cert=False
#     )
#     resp = yield client.fetch(request)
#     body = json.loads(resp.body)
#     short_url = body['short_url']
#     raise Return(short_url)

# @coroutine
# # @assert_user #@assert_user(roles=['admin','operator','master'])
# def get(self, activity_id):
#     event = yield self.fetchone_db("select * from t_news where id = %s", activity_id)
#     res = yield self.query_db(
#         '''SELECT email,cellphone FROM t_person tp left join t_traffic tt on tt.person_id = tp.person_id where tt.activity_id = {activity_id}'''.format(
#             activity_id=activity_id))
#     # for item in self.config:
#     #     print item, "  :  ",self.config[item].encode('utf-8')
#     # for item in res:
#     #     i = item['cellphone']
#     #     j = item['email'].encode('utf-8')
#     #     print i,j
#     # code = '18610807347'
#     # msg = self.config['event_cancel_msg']
#     # yield send_message(code, msg, self.config)
#     # emails = ['xprobie@gmail.com','517450974@qq.com','xprobie@outlook.com']
#     # title = u'【活动取消通知】工业大数据采集与分析-复旦大数据思享会'
#     # content = self.config['event_cancel_msg']
#     # self.config['noreply_mail_name'] = u'复旦大数据思享会'
#     # send_more_email(title, emails, content, self.config)
#     # send_email(title, email, content, self.config)
#     email_list = list()
#     for i in res:
#         email = i['email']
#         if email:
#             email_list.append(email)
#         else:
#             pass
#     title = u'【活动取消通知】工业大数据采集与分析-复旦大数据思享会'
#     content = self.config['event_cancel_msg']
#     self.config['noreply_mail_name'] = u'复旦大数据思享会'
#     try:
#         yield send_more_email(title, email_list, content, self.config)
#     except Exception as e:
#         logging.info(e)
#
#     for i in res:
#         cellphone = i['cellphone']
#         if cellphone:
#             code = cellphone.strip()
#             # code = '18610807347'
#             msg = self.config['event_cancel_msg']
#             yield send_message(code, msg, self.config)
#     yield self.restful({
#         'message': "活动取消的短信和邮箱已发送成功!^_^"
#     }
#     )


# 邮件审批流程
@Route(r"/rest/action")
class _(MgrHandler):
    '''
    这个类处理邮件审批会员申请的流程
    '''

    @coroutine
    def get(self):
        '''
        uuid : 每一封邮件对应一个uuid,通过uuid在cache里面取出action_info
        action_info 内容: 操作动作action,表单form_id,person_id,status(表单状态)
        :return:
        '''
        uuid = self.get_argument('uuid')
        entry = 'form_action'
        page = get_page_by_entry(entry)
        action_info = self.get_cache(uuid)
        if not action_info:
            self.render(page['layout'],
                        entry=entry,
                        page=page,
                        page_config=map_config,
                        context=u'该操作已过期')
            return
        infos = action_info.split('|')
        # 操作动作
        action = infos[0]
        # 要审核的表单id
        form_id = infos[1]
        person_id = infos[2]
        status = infos[3]

        advanced_member_list = yield self.member_type_list(advanced=True)
        normal_member_list = yield self.member_type_list(normal=True)
        person_member_list = yield self.member_type_list(person=True)
        form_info = yield self.fetchone_db("select * from t_form where form_id = %s", form_id)
        if form_info['apply_member_type'] in person_member_list:
            person_info = yield self.fetchone_db("""select p.cellphone from t_form_relation as fr
                                                                        inner join t_form as f
                                                                        on f.form_id = fr.form_id
                                                                        inner join t_org_person as op
                                                                        on fr.org_id=op.org_id and op.is_primary=0
                                                                        inner join t_person as p
                                                                        on fr.person_id=p.person_id
                                                                        where f.form_id=%s""", form_id)
        else:
            person_info = yield self.fetchone_db("""select p.cellphone from t_form_relation as fr
                                                                        inner join t_form as f
                                                                        on f.form_id = fr.form_id
                                                                        inner join t_org_person as op
                                                                        on fr.org_id=op.org_id and op.is_primary=1
                                                                        inner join t_person as p
                                                                        on op.person_id=p.person_id
                                                                        where f.form_id=%s""", form_id)

        if action == 'person_first_instance' or action == 'org_first_instance' or action == 'delete_apply':
            # 会员管理员
            res = yield self.fetchone_db("select * from t_auth_role where person_id=%s and role_id='operator'",
                                         person_id)
            if not res:
                self.render(page['layout'],
                            entry=entry,
                            page=page,
                            page_config=map_config,
                            # context=u'您已不是事务性管理员,无操作权限')
                            context=u'您无操作权限')
                return
            if action == 'person_first_instance' or action == 'org_first_instance':
                if form_info['form_status'] != 'submitted':
                    self.render(page['layout'],
                                entry=entry,
                                page=page,
                                page_config=map_config,
                                context=u'该条申请已被审核')
                    return
                yield self.update_db("update t_form set form_status = %s , vote_start_time = %s where form_id = %s",
                                     status, get_now_str(), form_id)
                message = str()
                if status == 'voting':
                    message = u'初审成功,通过该条申请'
                    yield send_email_to_manager(self, form_id, 'vote')
                    yield send_message(person_info['cellphone'], self.config['pass_first_instance'], self.config)
                elif status == 'reviewed_failed':
                    message = u'初审成功,退回该条申请'
                    yield send_message(person_info['cellphone'], self.config['not_pass_first_instance'], self.config)
                self.render(page['layout'],
                            entry=entry,
                            page=page,
                            page_config=map_config,
                            context=message)
            elif action == 'delete_apply':
                yield self.execute_db("delete from t_form where form_id=%s", form_id)
                yield self.execute_db("delete from t_form_relation where form_id=%s", form_id)
                self.render(page['layout'],
                            entry=entry,
                            page=page,
                            page_config=map_config,
                            context=u'已成功删除该会员申请')
            yield self.update_db("update t_form set form_status=%s , update_date=%s where form_id=%s", status,
                                 get_now_str(), form_id)
        elif action == 'vote':
            res = yield self.query_db("select * from t_vote_record where form_id=%s and person_id=%s", form_id,
                                      person_id)
            if res:
                self.render(page['layout'],
                            entry=entry,
                            page=page,
                            page_config=map_config,
                            context=u'您已投过票，不可重复投票')
                return
            args = {
                'form_id': form_id,
                'attitue': status,
                'message': '',
                'create_time': get_now_str(),
                'person_id': person_id,
                'auth_id': ''
            }
            if form_info['apply_member_type'] in normal_member_list:
                yield self.insert_db_by_obj('t_vote_record', args)
                number = yield self.fetchone_db(
                    "select count(1) as number from t_vote_record as v , t_auth_role as r where v.attitue='agree' and r.role_id='master' and r.person_id=v.person_id and v.form_id=%s",
                    form_id)
                member_fee = yield self.fetchone_db("select paid_money from t_form where form_id = %s", form_id)
                member_fee = int(member_fee['paid_money'])
                if number['number'] >= 1 and member_fee:
                    yield self.update_db(
                        "update t_form set form_status='votedsuccess',vote_success_time=%s where form_id = %s",
                        get_now_str(), form_id)
                    yield send_email_to_manager(self, form_id, 'charge')
                    yield send_message(person_info['cellphone'], self.config['pass_vote'], self.config)
                if number['number'] >= 1 and not member_fee:
                    yield self.update_db(
                        "update t_form set form_status='paid',vote_success_time=%s where form_id = %s",
                        get_now_str(), form_id)
                    if form_info['apply_member_type'] == 'normal_org_member':
                        org_id = person_info['org_id']
                        person_id = str()
                    else:
                        org_id = str()
                        person_id = person_info['person_id']
                    today = datetime.datetime.now()
                    next_year = today.replace(year=today.year + 1)
                    member_args = {
                        'member_id': generate_uuid(),
                        'person_id': person_id,
                        'org_id': org_id,
                        'create_date': today,
                        'due_date': next_year,
                        'form_id': form_id,
                        'status': 'valid',
                        'weixin_group': person_info['weixin_group'],
                        'member_type': form_info['apply_member_type'],
                        'certificate': 0
                    }
                    yield self.insert_db_by_obj("t_member", member_args)
            elif form_info['apply_member_type'] in advanced_member_list:
                yield self.insert_db_by_obj('t_vote_record', args)
            vote_attitude = str()
            if status == 'agree':
                vote_attitude = u'赞成加入'
            elif status == 'oppose':
                vote_attitude = u'反对加入'
            else:
                vote_attitude = u'已弃权'
            self.render(page['layout'],
                        entry=entry,
                        page=page,
                        page_config=map_config,
                        context=u'投票成功,%s' % vote_attitude)


# 未知代码,如果知道的话请写上备注
@Route(r"/rest/mgr/send/email")
class _(MgrHandler):
    @coroutine
    def get(self):
        # fr = open("tpl/test_email_newsletter.html","r")
        # content = fr.read()
        yield send_email_to_manager(self, '97d4d742-e791-11e5-a709-aabab5815e52', 'vote')
        yield self.restful({
            'message': True
        })


@coroutine
def clear_all_user_profiles(handler):
    users = yield handler.query_db("select person_id from t_person where length(person_id)>0")
    for u in users:
        handler.set_cache("user-profile-" + u['person_id'], '', 86400 * 300)


@Route(r"/rest/mgr/batchjobs")
class _(MgrHandler):
    '''
    每天进行的批量检查,比如会员过期,投票结束日期,重新刷新用户登录信息等
    '''

    @coroutine
    def get(self):
        start_time = get_now_str()
        yield check_vote_result(self)
        # yield check_expired_result(self)
        yield clear_all_user_profiles(self)
        end_time = get_now_str()
        yield self.restful({
            'result': 'Done from %s to %s' % (start_time, end_time)
        })


@Route(r"/rest/mgr/fetch/weixin")
class _(MgrHandler):
    @coroutine
    @assert_user
    #    @assert_user #@assert_user(roles=['admin','operator','master'])
    def post(self):
        url = self.get_argument('url')
        res = weixin_sogou.parse_essay(url)
        yield self.restful(res)


# 个人申请管理
@Route(r"/rest/mgr/form/table")
class _(MgrHandler):
    '''
    个人申请管理
    '''

    @assert_user  # @assert_user(roles=['admin','operator','master'])
    @coroutine
    def get(self):
        key = yield self.member_type_list(person=True)
        type_dict = dict()
        where_args = list()
        for i in key:
            type_dict[i] = self.get_argument(i, "")
            if len(str(type_dict[i])) > 0:
                where_args.append("f.apply_member_type='{apply_member_type}'".format(apply_member_type=i))
        where_args = " or ".join(where_args)
        if where_args:
            yield response_datatable_result(
                columns='f.form_code,f.apply_member_type,o.org_name,f.apply_date,f.vote_success_time,f.form_status,f.form_id,c1.code_name as apply_member_type_name,p.fullname,c2.code_name as form_status_name,f.vote_start_time,f.form_id,p.person_id'.split(
                    ','),
                table='''t_person as p
                        left join t_org_person as op
                        on op.person_id = p.person_id and op.is_primary = 0
                        left join t_org as o
                        on o.org_id = op.org_id
                        left join t_form_relation as fr
                        on fr.person_id = p.person_id
                        left join t_form as f
                        on f.form_id = fr.form_id
                        left join t_codes as c1
                        on c1.code_id = f.apply_member_type and c1.code_type = "member_type"
                        left join t_codes as c2
                        on c2.code_id = f.form_status and c2.code_type="form_status"''',
                sortcol='f.apply_date DESC',
                req=self,
                searchcolumns='f.form_code,o.org_name,p.fullname,c2.code_name',
                where="(f.form_status <> 'deleted' and f.form_status <> 'weixin' and f.form_status <> 'paid') and ({where_args})".format(
                    where_args=where_args))
        else:
            yield response_datatable_result(
                columns='f.form_code,f.apply_member_type,o.org_name,f.apply_date,f.vote_success_time,f.form_status,f.form_id,c1.code_name as apply_member_type_name,p.fullname,c2.code_name as form_status_name,f.vote_start_time,f.form_id,p.person_id'.split(
                    ','),
                table='''t_person as p
                                left join t_org_person as op
                                on op.person_id = p.person_id and op.is_primary = 0
                                left join t_org as o
                                on o.org_id = op.org_id
                                left join t_form_relation as fr
                                on fr.person_id = p.person_id
                                left join t_form as f
                                on f.form_id = fr.form_id
                                left join t_codes as c1
                                on c1.code_id = f.apply_member_type
                                left join t_codes as c2
                                on c2.code_id = f.form_status and c2.code_type="form_status"''',
                sortcol='f.apply_date DESC',
                req=self,
                searchcolumns='f.form_code,o.org_name,p.fullname,c2.code_name',
                where="(f.form_status <> 'deleted' and f.form_status <> 'weixin' and f.form_status <> 'paid') and (f.apply_member_type='weixin_group' or f.apply_member_type='normal_member' or f.apply_member_type='advanced_member')")


# 企业申请管理
@Route(r"/rest/mgr/org/form/table")
class _(MgrHandler):
    @assert_user  # @assert_user(roles=['admin','operator','master'])
    @coroutine
    def get(self):
        key = yield self.member_type_list(org=True)
        type_dict = dict()
        where_args = list()
        for i in key:
            type_dict[i] = self.get_argument(i, "")
            if len(str(type_dict[i])) > 0:
                where_args.append("f.apply_member_type='{apply_member_type}'".format(apply_member_type=i))
        where_args = " or ".join(where_args)
        if where_args:
            yield response_datatable_result(
                columns="""f.form_code|f.apply_member_type|o.org_name|f.apply_date|c2.code_name as form_status_name|f.form_status|f.vote_success_time|f.vote_start_time|f.form_id|c1.code_name as apply_member_type_name|GROUP_CONCAT(DISTINCT p.fullname Separator ',') as primaries|p.fullname|p.person_id|o.org_id""".split(
                    '|'),
                table="""t_org as o
                        left join t_org_person as op
                        on op.org_id=o.org_id
                        left join t_person p
                        on op.person_id=p.person_id
                        left join t_form_relation as fr
                        on fr.org_id = op.org_id
                        left join t_form as f
                        on f.form_id = fr.form_id
                        LEFT JOIN t_codes as c1
                        ON c1.code_id = f.apply_member_type
                        LEFT JOIN t_codes as c2
                        on c2.code_id = f.form_status""",
                sortcol='f.apply_date DESC',
                req=self,
                searchcolumns='f.form_code,o.org_name,p.fullname,c2.code_name,p.cellphone',
                where='''(f.form_status <> 'deleted' and f.form_status <> 'paid')
                                   and fr.org_id = op.org_id
                                   and op.is_primary = 1
                                   and op.org_id = o.org_id
                                   and  ({where_args}) GROUP BY op.org_id'''.format(where_args=where_args))
        else:
            yield response_datatable_result(
                columns="f.form_code|f.apply_member_type|o.org_name|f.apply_date|c2.code_name as form_status_name|f.form_status|f.vote_success_time|f.vote_start_time|f.form_id|c1.code_name as apply_member_type_name|GROUP_CONCAT(DISTINCT p.fullname Separator ',') as primaries|p.fullname|p.person_id|o.org_id".split(
                    '|'),
                table='''t_org as o
                        left join t_org_person as op
                        on op.org_id=o.org_id
                        left join t_person p
                        on op.person_id=p.person_id
                        left join t_form_relation as fr
                        on fr.org_id = op.org_id
                        left join t_form as f
                        on f.form_id = fr.form_id
                        LEFT JOIN t_codes as c1
                        ON c1.code_id = f.apply_member_type
                        LEFT JOIN t_codes as c2
                        on c2.code_id = f.form_status
                                                               ''',
                sortcol='f.apply_date DESC',
                req=self,
                searchcolumns='f.form_code,o.org_name,p.fullname,c2.code_name,p.cellphone',
                where='''(f.form_status <> 'deleted' and f.form_status <> 'paid')
                                   and fr.org_id = op.org_id
                                   and op.is_primary = 1
                                   and op.org_id = o.org_id
                                   and (f.apply_member_type='advanced_org_member' or f.apply_member_type='normal_org_member') group by op.org_id''')


@Route(r"/rest/mgr/edit/status")
class _(MgrHandler):
    '''
    会员申请表单状态修改
    '''

    @assert_user
    @coroutine
    def post(self):
        form_id = self.get_argument("form_id", "")
        status = self.get_argument("form_status", "")
        person_info = yield self.fetchone_db("""select p.cellphone from t_form as f , t_person as p ,
                t_form_relation as fr left join t_org_person as op on fr.org_id=op.org_id and op.is_primary=1 where f.form_id=fr.form_id and fr.person_id=p.person_id and f.form_id=%s""",
                                             form_id)
        yield self.update_db("update t_form set form_status=%s where form_id=%s", status, form_id)
        if status == 'votedfailed':
            yield send_message(person_info['cellphone'], self.config['not_pass_vote'], self.config)
        yield self.restful({
            "message": "修改成功"
        })


@Route(r"/rest/mgr/form/paid")
class _(MgrHandler):
    @assert_user  # @assert_user(roles=['operator'])
    @coroutine
    def post(self):
        form_id = self.get_argument('form_id')
        start_time = self.get_argument('start_time')
        end_time = self.get_argument('end_time')
        paid_number = self.get_argument('paid_number')
        paid_money = self.get_argument('paid_money')
        try:
            paid_money = int(paid_money)
        except:
            yield self.error("付费金额必须为数字")
            return
        paid_type = self.get_argument('paid_type')
        paid_pictures = self.get_argument('paid_pictures')
        try:
            start = datetime.datetime.strptime(start_time, '%Y-%m-%d')
            end = datetime.datetime.strptime(end_time, '%Y-%m-%d')
        except:
            yield self.error("日期格式错误")
            return
        status = yield self.fetchone_db("select form_status ,apply_member_type from t_form where form_id = %s", form_id)
        args = {
            'form_status': 'paid',
            'paid_start_time': start_time,
            'paid_end_time': end_time,
            'paid_money': paid_money,
            'paid_number': paid_number,
            'paid_type': paid_type,
            'paid_pictures': paid_pictures
        }
        yield self.update_db_by_obj('t_form', args, "form_id='%s'" % form_id)
        paid_record_args = {
            'form_id': form_id,
            'paid_start_time': start_time,
            'paid_end_time': end_time,
            'paid_money': paid_money,
            'paid_number': paid_number,
            'paid_type': paid_type,
            'paid_pictures': paid_pictures,
            'paid_remark': self.get_argument('paid_remark', ''),
            'created': get_now_str(),
            'updated': get_now_str()
        }
        yield self.insert_db_by_obj('t_payment_record', paid_record_args)
        person_member_type = yield self.member_type_list(person=True)
        org_member_type = yield self.member_type_list(org=True)
        relative = list()
        person_member = False
        org_member = False
        if status['apply_member_type'] in person_member_type:
            # 如果是个人会员付费，is_primary = 0
            person_member = True
            relative = yield self.fetchone_db("""
                                            select p.person_id from t_person as p
                                            left join t_org_person as op on p.person_id = op.person_id
                                            left join t_form_relation as fr on fr.person_id = op.person_id
                                            where fr.form_id=%s""", form_id)
        elif status['apply_member_type'] in org_member_type:
            # 如果是企业会员付费，is_primary = 1
            org_member = True
            relative = yield self.fetchone_db("""
                                        select op.org_id from t_person as p
                                        left join t_org_person as op on p.person_id = op.person_id
                                        left join t_form_relation as fr on fr.org_id = op.org_id
                                        left join t_form as f on f.form_id = fr.form_id
                                        where op.is_primary = 1 and f.form_id=%s""", form_id)
        else:
            yield self.error("没有此会员类型")
            return
        if person_member:
            res = yield self.fetchone_db("select * from t_member where person_id=%s", relative['person_id'])
            if res:
                member_info = {
                    'create_date': get_now_str(),
                    'form_id': form_id,
                    'due_date': end_time,
                    'member_type': status['apply_member_type']
                }
                yield self.update_db_by_obj("t_member", member_info, "member_id='%s'" % res['member_id'])
            else:
                member_info = {
                    'member_id': generate_uuid(),
                    'person_id': relative['person_id'],
                    'status': 'valid',
                    'create_date': get_now_str(),
                    'org_id': '',
                    'form_id': form_id,
                    'due_date': end_time,
                    'member_type': status['apply_member_type'],
                    'auth_id': ''
                }
                yield self.insert_db_by_obj('t_member', member_info)
        elif org_member:
            res = yield self.fetchone_db("select * from t_member where org_id=%s", relative['org_id'])
            if res:
                member_info = {
                    'create_date': get_now_str(),
                    'form_id': form_id,
                    'due_date': end_time,
                    'member_type': status['apply_member_type']
                }
                yield self.update_db_by_obj("t_member", member_info, "member_id='%s'" % res['member_id'])
            else:
                member_info = {
                    'member_id': generate_uuid(),
                    'person_id': '',
                    'status': 'valid',
                    'create_date': get_now_str(),
                    'org_id': relative['org_id'],
                    'form_id': form_id,
                    'due_date': end_time,
                    'member_type': status['apply_member_type'],
                    'auth_id': ''
                }
                yield self.insert_db_by_obj('t_member', member_info)
        else:
            yield self.error('没有此会员类型')
        yield self.restful({
            'message': '修改状态成功'
        })


@Route(r"/rest/mgr/form/paid/edit")
class _(MgrHandler):
    @assert_user  # @assert_user(roles=['operator'])
    @coroutine
    def post(self):
        id = self.get_argument('id')
        start_time = self.get_argument('start_time')
        end_time = self.get_argument('end_time')
        paid_number = self.get_argument('paid_number')
        try:
            paid_money = int(self.get_argument('paid_money'))
        except:
            yield self.error("付费金额必须为数字")
            return
        paid_type = self.get_argument('paid_type')
        paid_pictures = self.get_argument('paid_pictures')
        try:
            start = datetime.datetime.strptime(start_time, '%Y-%m-%d')
            end = datetime.datetime.strptime(end_time, '%Y-%m-%d')
        except:
            yield self.error("日期格式错误")
            return
        status = yield self.fetchone_db(
            "select t.form_status ,t.apply_member_type,t.form_id from t_form as t ,t_payment_record as p where t.form_id = p.form_id and p.id=%s",
            id)
        args = {
            'form_status': 'paid',
            'paid_start_time': start_time,
            'paid_end_time': end_time,
            'paid_money': paid_money,
            'paid_number': paid_number,
            'paid_type': paid_type,
            'paid_pictures': paid_pictures
        }
        form_id = status['form_id']
        yield self.update_db_by_obj('t_form', args, "form_id='%s'" % form_id)
        paid_record_args = {
            'paid_start_time': start_time,
            'paid_end_time': end_time,
            'paid_money': paid_money,
            'paid_number': paid_number,
            'paid_type': paid_type,
            'paid_pictures': paid_pictures,
            'updated': get_now_str(),
            'paid_remark': self.get_argument("paid_remark", "")
        }
        yield self.update_db_by_obj('t_payment_record', paid_record_args, "id='%s'" % id)
        relative = yield self.query_db("select person_id , org_id from t_form_relation where form_id=%s", form_id)
        # auth_id = ''
        # for item in relative:
        #     res = yield self.fetchone_db("select * from t_member where person_id=%s", item['person_id'])
        #     if res:
        #         # yield self.query_db('delete from t_form where form_id=%s',res['form_id'])
        #         # yield self.query_db('delete from t_form_relation where form_id=%s',res['form_id'])
        #         member_info = {
        #             'create_date': get_now_str(),
        #             'form_id': form_id,
        #             'due_date': end_time,
        #             'member_type': status['apply_member_type']
        #         }
        #         yield self.update_db_by_obj("t_member", member_info, "member_id='%s'" % res['member_id'])
        #     else:
        #         member_info = {
        #             'member_id': generate_uuid(),
        #             'status': 'valid',
        #             'create_date': get_now_str(),
        #             'person_id': item['person_id'],
        #             'org_id': item['org_id'],
        #             'form_id': form_id,
        #             'due_date': end_time,
        #             'member_type': status['apply_member_type'],
        #             'auth_id': auth_id
        #         }
        #         yield self.insert_db_by_obj('t_member', member_info)
        yield self.restful({
            'message': '修改状态成功'
        })


@Route(r"/rest/mgr/form/delete")
class _(MgrHandler):
    '''
    会员申请表单删除
    '''

    @assert_user
    @coroutine  # @assert_user(roles=['admin','operator','master'])
    def get(self):
        form_id = self.get_argument('form_id')
        yield self.execute_db("delete from t_form_relation where form_id = %s", form_id)
        yield self.execute_db("delete from t_form where form_id = %s", form_id)
        yield self.restful({
            'message': '删除成功'
        })


@Route(r"/rest/mgr/admin/delete")
class _(MgrHandler):
    '''
    内部人员管理的删除
    '''

    @assert_user
    @coroutine
    # @assert_user(roles=['admin'])
    def post(self):
        person_id = self.get_argument('person_id')
        yield self.execute_db("delete from t_auth_role where person_id = %s", person_id)
        yield self.restful({
            'message': '删除成功'
        })


# 通过手机号查找其关联的企业
@Route(r"/rest/admin/cellphone/person_info")
class _(MgrHandler):
    @assert_user
    @coroutine
    def post(self):
        cellphone = self.get_argument("cellphone")
        org_info = list()
        if cellphone:
            res = yield self.fetchone_db("""select * from t_person where cellphone = %s""", cellphone)
            if not res:
                self.restful({
                    "message": 'false'
                })
            else:
                person_info = yield self.fetchone_db("""select fullname,nick_name,GROUP_CONCAT(DISTINCT o.org_name Separator ', ') as org_names,GROUP_CONCAT(DISTINCT t.title_name Separator ', ') as title_names from t_org as o
                                            left join t_org_person as op on o.org_id = op.org_id left join t_title as t on t.title_id = op.title_id
                                            left join t_person as p on op.person_id = p.person_id where p.cellphone = %s group by p.person_id""",
                                                     cellphone)
                org_names = person_info['org_names'].split(',')
                title_names = person_info['title_names'].split(',')
                for i in range(0, len(org_names) - len(title_names)):
                    title_names.append('未填写')
                for org_name, title_name in zip(org_names, title_names):
                    org_info.append(str(org_name) + ' ( ' + str(title_name) + ' ) ')
                name_info = str(person_info['fullname']) + ' ( ' + str(person_info['nick_name']) + ' ) '
                self.restful({
                    "org_info": org_info,
                    "name_info": name_info,
                    "message": 'true'
                })
        else:
            pass


# 内部人员管理、增加权限
@Route(r"/rest/mgr/admin/add")
class _(MgrHandler):
    @assert_user
    @coroutine
    def post(self):
        cellphone = self.get_argument('cellphone')
        roles = self.get_argument('roles')
        group_name = self.get_argument('group_name')
        res = yield self.query_db(
            "select * from t_auth_role as r , t_person as a where a.person_id = r.person_id and a.cellphone=%s",
            cellphone)
        if len(res) > 0:
            yield self.error("该用户已为管理员。如果是为已有管理员增加权限请在列表中选择对应人员。")
        res = yield self.query_db("select person_id,auth_id from t_person where cellphone=%s", cellphone)
        if len(res) == 0:
            yield self.error("该手机号码未绑定微信账号")
        org_res = yield self.fetchone_db("""select * from t_org where org_name = %s""", group_name)
        group_id = ''
        if org_res:
            group_id = org_res['org_id']
        else:
            group_id = generate_uuid()
        group_res = yield self.fetchone_db("select * from t_group where group_id = %s and group_name = %s", group_id,
                                           group_name)
        if not group_res:
            # TODO 现在代码写死parent_id（微董会）和level
            group_args = {
                'group_id': group_id,
                'group_name': group_name,
                'level': 1,
                'parent_id': "7217ed7f-e485-4ac8-ac9a-4b8027aeb7dd"
            }
            yield self.insert_db_by_obj("t_group", group_args)
        all_roles = roles.split(',')
        for item in all_roles:
            data = {
                "role_id": item
                , "person_id": res[0]['person_id']
                , "group_id": group_id
            }
            yield self.insert_db_by_obj('t_auth_role', data)
        yield self.restful({
            'message': '添加成功'
        })


@Route(r"/rest/mgr/admin/edit/roles")
class _(MgrHandler):
    @assert_user
    @coroutine
    def post(self):
        person_id = self.get_argument('person_id')
        roles = self.get_argument('roles')
        yield self.query_db('delete from t_auth_role where person_id =%s', person_id)
        all_roles = roles.split(',')
        for item in all_roles:
            data = {
                "role_id": item,
                "person_id": person_id
            }
            yield self.insert_db_by_obj('t_auth_role', data)
        yield self.restful({
            'message': '修改成功'
        })


@Route(r"/rest/mgr/roles/edit/pages")
class _(MgrHandler):
    @assert_user
    @coroutine
    def post(self):
        user = self.current_user_profile
        user_auth_id = user['authorized']['auth_id']
        role_id = self.get_argument('role_id')
        pages = self.get_argument('pages')
        yield self.query_db('delete from t_role_page where role_id =%s', role_id)
        all_pages = pages.split(',')
        for item in all_pages:
            data = {
                "role_id": role_id,
                "page_id": item,
                "created": get_now_str()
            }
            yield self.insert_db_by_obj('t_role_page', data)
        yield self.restful({
            'message': '修改成功'
        })


@Route(r"/rest/mgr/form/examine")
class _(MgrHandler):
    @assert_user  # @assert_user(roles=['operator'])
    @coroutine
    def post(self):
        form_id = self.get_argument('form_id')
        status = self.get_argument('status')
        if not auth.check_auth(self, roles=['operator']):
            yield self.error("您非事务性管理员，无法审批")
            return
        if status in ['reviewed_success', 'reviewed_failed', 'voting']:
            person_info = yield self.fetchone_db("""select p.cellphone from t_form as f
                                                    left join t_form_relation as fr
                                                    on f.form_id = fr.form_id
                                                    left join t_org_person as op
                                                    on fr.org_id=op.org_id and op.is_primary=1
                                                    left join t_person as p
                                                    on p.person_id = op.person_id
                                                    where f.form_id=%s""", form_id)

            if status == 'voting':
                yield self.update_db("update t_form set form_status = %s , vote_start_time=%s where form_id =%s",
                                     status, get_now_str(), form_id)
                yield send_message(person_info['cellphone'], self.config['pass_first_instance'], self.config)
                yield send_email_to_manager(self, form_id, 'vote')
            elif status == 'reviewed_failed':
                yield send_message(person_info['cellphone'], self.config['not_pass_first_instance'], self.config)
                yield self.update_db("update t_form set form_status = %s where form_id =%s", status, form_id)
            yield self.response_as_json({'message': '审批成功'})
        else:
            yield self.error("请求不合理")


@Route(r"/rest/mgr/check/vote/role")
class _(MgrHandler):
    @assert_user
    # @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self):
        form_id = self.get_argument('form_id')
        # 查找数据库中的所有非理事会员
        normal_member = yield self.query_db(
            "select code_id from t_codes where code_type='member_type' and code_id not like '%%advanced%%'")
        normal_member_list = [x['code_id'] for x in normal_member]
        # 查找数据库中的所有理事会员
        advanced_member = yield self.query_db(
            "select code_id from t_codes where code_type='member_type' and code_id like '%%advanced%%'")
        advanced_member_list = [x['code_id'] for x in advanced_member]
        res = yield self.query_db("select * from t_vote_record where form_id=%s and person_id=%s", form_id,
                                  self.current_user)
        if res:
            yield self.error("您已投过票，不可重复投票")
            return
        form_info = yield self.fetchone_db("select * from t_form where form_id = %s", form_id)
        if form_info:
            if form_info['apply_member_type'] in normal_member_list:
                if not auth.check_auth(self, roles=['master']):
                    yield self.error("您非秘书处成员，无投票权")
                    return
                else:
                    yield self.response_as_json({'message': True})
                    return
            elif form_info['apply_member_type'] in advanced_member_list:
                if not auth.check_auth(self, roles=['master']) and not auth.check_auth(self,
                                                                                       members=advanced_member_list):
                    yield self.error("您不是理事会员,也不是秘书处成员,无投票权限")
                    return
                else:
                    yield self.response_as_json({'message': True})
                    return
            else:
                yield self.error("没有此会员类型")
                return
        else:
            yield self.error("没有此申请表")
            return


# 会员申请投票
@Route(r"/rest/mgr/vote")
class _(MgrHandler):
    @assert_user
    @coroutine
    def post(self):
        form_id = self.get_argument('form_id')

        # 查找数据库中的所有非理事会员
        normal_member_list = yield self.member_type_list(normal=True)
        # 查找数据库中的所有理事会员
        advanced_member_list = yield self.member_type_list(advanced=True)

        # 登陆者是否已经投票
        res = yield self.fetchone_db("select * from t_vote_record where form_id=%s and person_id=%s", form_id,
                                     self.current_user)
        if res:
            yield self.error("您已投过票，不可重复投票")
            return
        form_info = yield self.fetchone_db("select * from t_form where form_id = %s", form_id)
        if form_info['apply_member_type'] in normal_member_list:
            if not auth.check_auth(self, roles=['master']):
                yield self.error("您非秘书处成员，无投票权")
                return
        elif form_info['apply_member_type'] in advanced_member_list:
            if not auth.check_auth(self, roles=['master']) and not auth.check_auth(self, members=advanced_member_list):
                yield self.error("您不是理事会员,也不是秘书处成员,无投票权限")
                return

        form_id = self.get_argument('form_id')
        attitue = self.get_argument('attitue')
        message = self.get_argument('reason')
        profile = self.current_user_profile
        auth_id = profile['authorized']['auth_id']
        form_info = yield self.fetchone_db("select * from t_form where form_id = %s", form_id)
        args = {
            'form_id': form_id,
            'attitue': attitue,
            'message': message,
            'create_time': get_now_str(),
            'auth_id': auth_id
            , 'person_id': self.current_user
        }
        person_info = yield self.fetchone_db("""select p.cellphone,p.person_id,p.weixin_group,op.org_id from t_form as f , t_person as p ,
                t_form_relation as fr left join t_org_person as op on fr.org_id=op.org_id and op.is_primary=1 where f.form_id=fr.form_id and fr.person_id=p.person_id and f.form_id=%s""",
                                             form_id)

        if form_info['apply_member_type'] in normal_member_list:
            yield self.insert_db_by_obj('t_vote_record', args)
            number = yield self.fetchone_db(
                "select count(1) as number from t_vote_record as v , t_auth_role as r where v.attitue='agree' and r.role_id='master' and r.person_id=v.person_id and v.form_id=%s",
                form_id)
            member_fee = yield self.fetchone_db("select paid_money from t_form where form_id = %s", form_id)
            member_fee = int(member_fee['paid_money'])
            if number['number'] >= 1 and member_fee:
                yield self.update_db(
                    "update t_form set form_status='votedsuccess',vote_success_time=%s where form_id = %s",
                    get_now_str(), form_id)
                yield send_message(person_info['cellphone'], self.config['pass_vote'], self.config)
            if number['number'] >= 1 and not member_fee:
                yield self.update_db(
                    "update t_form set form_status='paid',vote_success_time=%s where form_id = %s",
                    get_now_str(), form_id)
                if form_info['apply_member_type'] == 'normal_org_member':
                    org_id = person_info['org_id']
                    person_id = ''
                else:
                    org_id = ''
                    person_id = person_info['person_id']
                today = datetime.datetime.now()
                next_year = today.replace(year=today.year + 1)
                member_args = {
                    'member_id': generate_uuid(),
                    'person_id': person_id,
                    'org_id': org_id,
                    'create_date': today,
                    'due_date': next_year,
                    'form_id': form_id,
                    'status': 'valid',
                    'weixin_group': person_info['weixin_group'],
                    'member_type': form_info['apply_member_type'],
                    'certificate': 0
                }
                yield self.insert_db_by_obj("t_member", member_args)
        elif form_info['apply_member_type'] in advanced_member_list:
            yield self.insert_db_by_obj('t_vote_record', args)
        yield self.response_as_json({'message': '投票成功'})


@Route(r"/rest/mgr/vote/detail/table")
class _(MgrHandler):
    @coroutine
    def get(self):
        form_id = self.get_argument('form_id')
        yield response_datatable_result(columns='u.fullname,c.code_name as attitue,r.create_time,r.message'.split(','),
                                        table='''t_vote_record as r left join t_codes as c on c.code_id = r.attitue
                                                      left join t_person as u on u.person_id = r.person_id
                                                    ''',
                                        sortcol='a.apply_date DESC',
                                        req=self,
                                        searchcolumns='',
                                        where="""r.form_id = '%s'""" % form_id)


# 详情
@Route(r"/rest/mgr/org/form/detail")
class _(MgrHandler):
    """企业会员申请表单详情"""

    @assert_user
    @coroutine
    def get(self):
        form_id = self.get_argument('form_id')
        person_info = yield self.query_db("""select p.*,op.org_id from t_person as p
                                            left join t_org_person as op
                                            on p.person_id = op.person_id and op.is_primary = 1
                                            left join t_form_relation as fr
                                            on op.org_id = fr.org_id
                                            left join t_form as f
                                            on f.form_id = fr.form_id
                                            where f.form_status != 'weixin' and f.form_status != 'paid' and f.form_status != 'deleted'
                                            and f.form_id = %s""", form_id)
        org_info = yield self.query_db("select * from t_org where org_id = %s", person_info[0]['org_id'])
        yield self.restful({
            'person': person_info,
            'org': org_info
        })


# 详情
@Route(r"/rest/mgr/person/form/detail")
class _(MgrHandler):
    """个人会员申请表单详情"""

    @assert_user
    @coroutine
    def get(self):
        form_id = self.get_argument('form_id')
        person_info = yield self.query_db("""select p.*,op.org_id from t_person as p
                                            left join t_org_person as op
                                            on p.person_id = op.person_id
                                            left join t_form_relation as fr
                                            on op.person_id = fr.person_id
                                            left join t_form as f
                                            on f.form_id = fr.form_id
                                            where f.form_status != 'weixin' and f.form_status != 'paid' and f.form_status != 'deleted'
                                            and f.form_id = %s""", form_id)
        # person_id = person_info[0]['person_id']
        org_info = yield self.query_db("select * from t_org where org_id = %s", person_info[0]['org_id'])
        yield self.restful({
            'person': person_info,
            'org': org_info
        })


# 会员支付详情
@Route(r"/rest/mgr/paid/detail")
class _(MgrHandler):
    @assert_user
    @coroutine
    def get(self):
        id = self.get_argument('id')
        # 企业会员
        res = yield self.query_db(
            """select m.form_id,pr.id,left(pr.paid_start_time,10) as paid_start_time,left(pr.paid_end_time,10) as paid_end_time, pr.paid_money,pr.paid_number,c.code_name as paid_type,paid_remark
               from t_member as m
               inner join t_payment_record as pr
               on m.form_id = pr.form_id
               inner join t_codes as c
               on c.code_id = pr.paid_type
               where m.org_id=%s and c.code_type='paid_type' order by pr.paid_end_time""",
            id)
        if not res:
            # 个人会员
            res = yield self.query_db(
                """select m.form_id,pr.id,left(pr.paid_start_time,10) as paid_start_time,left(pr.paid_end_time,10) as paid_end_time, pr.paid_money,pr.paid_number,c.code_name as paid_type,paid_remark
				   from t_member as m
				   inner join t_payment_record as pr
				   on m.form_id = pr.form_id
				   inner join t_codes as c
				   on c.code_id = pr.paid_type and c.code_type='paid_type'
				   where m.person_id=%s  order by pr.paid_end_time""",
                id)
        yield self.restful(res)


@Route(r"/rest/mgr/paid/id")
class _(MgrHandler):
    @assert_user
    @coroutine
    def get(self):
        id = self.get_argument('id')
        res = yield self.fetchone_db(
            "select id,left(paid_start_time,10) as paid_start_time,left(paid_end_time,10) as paid_end_time, paid_money,paid_number,paid_pictures,paid_remark from t_payment_record where id = %s",
            int(id))
        yield self.restful(res)


@Route(r"/rest/mgr/paid/delete")
class _(MgrHandler):
    @assert_user
    @coroutine
    def post(self):
        id = self.get_argument('id')
        res = yield self.query_db("delete from t_payment_record where id = %s", id)
        yield self.restful({
            "message": "删除成功"
        })


@Route(r"/rest/mgr/form/remove")
class _(MgrHandler):
    @assert_user
    @coroutine
    def post(self):
        form_id = self.get_argument("form_id", "")
        person_id = self.get_argument("person_id", "")
        form_relation = yield self.query_db("select * from t_form_relation where form_id=%s", form_id)
        # if form_relation:
        #     form_relation = yield self.query_db("select * from t_form_relation where form_id=%s and person_id!=%s",
        #                                         form_id, person_id)
        if len(form_relation) <= 1:
            yield self.error("企业会员的成员不可为空")
            return
        else:
            # yield self.update_db("update t_member set org_id=%s , person_id=%s where form_id=%s",
            #                      form_relation[0]['org_id'], form_relation[0]['person_id'], form_id)
            # yield self.update_db("update t_org_person set is_primary=1 where person_id=%s and org_id=%s",
            #                      form_relation[0]['person_id'], form_relation[0]['org_id'])
            yield self.update_db("update t_org_person set is_primary=0 where person_id=%s and org_id=%s", person_id,
                                 form_relation[0]['org_id'])

            yield self.execute_db("delete from t_form where form_id=%s and person_id=%s", form_id, person_id)
            yield self.execute_db("delete from t_form_relation where form_id=%s and person_id=%s", form_id, person_id)
            yield self.restful({"message": "移除成功"})


@Route(r"/rest/mgr/org/remove")
class _(MgrHandler):
    @assert_user
    @coroutine
    def post(self):
        org_id = self.get_argument("org_id", "")
        person_id = self.get_argument("person_id", "")
        yield self.update_db("update t_org_person set is_primary=0 where person_id=%s and org_id=%s",
                             person_id, org_id)
        yield self.restful({"message": "移除成功"})


# 通过手机号添加企业成员
@Route(r"/rest/mgr/org/add/cellphone")
class _(MgrHandler):
    @assert_user
    @coroutine
    def post(self):
        org_id = self.get_argument("org_id", "")
        cellphone = self.get_argument("cellphone", "")
        is_primary = self.get_argument("is_primary", "")
        if not org_id or not cellphone or not is_primary:
            yield self.error("请输入必选项!")
            return
        person = yield self.fetchone_db("""select p.person_id,op.org_id,op.is_primary from t_person as p
                                            left join t_org_person as op
                                            on op.person_id = p.person_id and op.org_id = %s
                                            where p.cellphone = %s""", org_id, cellphone)
        if not person:
            yield self.error("系统未有此手机号用户")
            return
        if person['org_id'] and person['org_id'] == org_id:
            yield self.update_db("update t_org_person set is_primary = %s where org_id = %s", is_primary, org_id)
        else:
            op_args = {
                'org_id': org_id,
                'person_id': person['person_id'],
                'is_primary': is_primary
            }
            yield self.insert_db_by_obj("t_org_person", op_args)
        yield self.restful({"message": "添加成功"})


@Route(r"/rest/mgr/org/add/person")
class _(MgrHandler):
    @assert_user
    @coroutine
    def post(self):
        person_args = self.get_args({
            'fullname': '*',
            'gender': '*',
            'cellphone': '*',
            'email': '*',
            'address': '',
            'school': '',
            'school_start': '',
            'education': '',
            'person_info': '',
            'birthday': '',
            'wechatid': '',
            'position': '',
            'expects': '',
            'wills': ''

        })
        if not person_args:
            yield self.error("请输入所有必填项")
            return
        if not is_valid_phone(person_args['cellphone']):
            yield self.error("手机号格式错误")
            return
        person = yield self.query_db("select * from t_person where cellphone=%s", person_args['cellphone'])
        if person:
            yield self.error("该手机号码已存在")
            return
        org_id = self.get_argument("org_id", "")
        if org_id:
            person_args['person_id'] = generate_uuid()
            org_person = {
                'org_id': org_id,
                'person_id': person_args['person_id'],
                'is_primary': 1
            }
            person_res = yield self.insert_db_by_obj("t_person", person_args)
            org_person_res = yield self.insert_db_by_obj("t_org_person", org_person)
            if person_res and org_person_res:
                yield self.restful({"message": "添加成功"})
            else:
                yield self.error({"message": "添加失败"})
        else:
            yield self.error({"message": "添加失败"})


# 个人(会员或者非会员)的详情信息
@Route(r"/rest/mgr/person/info/detail")
class _(MgrHandler):
    @assert_user
    @coroutine
    def get(self):
        person_id = self.get_argument('person_id', '')
        person_info = yield self.query_db("select * from t_person where person_id = %s", person_id)
        org_info = yield self.query_db("""select o.* from t_person as p
                                    left join t_org_person as op
                                    on p.person_id = op.person_id
                                    left join t_org as o
                                    on op.org_id = o.org_id
                                    where p.person_id = '%s'""" % person_id)
        person_type = 'not_member'
        member_info = yield self.query_db(
            "select left(due_date,10) as due_date,member_id,weixin_group,certificate,member_type,code_name as member_type_name,status from t_member as m left join t_codes on m.member_type=t_codes.code_id where m.person_id=%s",
            person_id)
        if member_info:
            person_type = 'member'

        weixin_group = yield self.query_db(
            "select tag_name as tag_id,tag_name from t_tag where tag_type = 'weixin_group'")

        form_info = yield self.fetchone_db('''select *,c1.code_name as apply_member_type,c2.code_name as paid_type from t_member as m
                                              left join t_form as f on m.form_id = f.form_id
                                              left join t_codes as c1 on c1.code_id = f.apply_member_type
                                              left join t_codes as c2 on c2.code_id = f.paid_type
                                              where c1.code_type = 'member_type'
                                              and c2.code_type = 'paid_type'
                                              and m.person_id = %s''', person_id)
        res = {
            'person': person_info,
            'org': org_info,
            'member': member_info,
            'weixin_group': weixin_group,
            'form': form_info,
            'type': person_type
        }

        yield self.restful(res)


# 企业详情
@Route(r"/rest/mgr/org/member/detail")
class _(MgrHandler):
    @assert_user
    @coroutine
    def get(self):
        org_id = self.get_argument('org_id')
        org_type = 'not_member'
        person = yield self.fetchone_db(
            "select p.* from t_person as p left join t_org_person as op on p.person_id = op.person_id where op.is_primary = 1 and op.org_id = %s",
            org_id)
        member = yield self.query_db(
            "select left(due_date,10) as due_date,member_id,weixin_group,certificate,member_type,code_name as member_type_name,status from t_member as m left join t_codes on m.member_type=t_codes.code_id where m.org_id=%s",
            org_id)
        if member:
            org_type = 'member'
        form_info = yield self.fetchone_db('''select *,c1.code_name as apply_member_type,c2.code_name as paid_type from t_member as m
                                                      left join t_form as f on m.form_id = f.form_id
                                                      left join t_codes as c1 on c1.code_id = f.apply_member_type
                                                      left join t_codes as c2 on c2.code_id = f.paid_type
                                                      where c1.code_type = 'member_type'
                                                      and c2.code_type = 'paid_type'
                                                      and m.org_id = %s''', org_id)
        org = yield self.fetchone_db("select * from t_org where org_id=%s", org_id)
        yield self.restful({
            'org': org,
            'form': form_info,
            'person': person,
            'member': member,
            'type': org_type
        })


# 人员管理修改
@Route(r"/rest/mgr/person/member/detail")
class _(MgrHandler):
    @assert_user
    @coroutine
    def get(self):
        person_id = self.get_argument('person_id', '')
        member_relative = yield self.fetchone_db(
            """select m.member_id,m.org_id ,m.person_id
            from t_person as p left join t_member as m on m.person_id = p.person_id
            where m.person_id=%s""", person_id)
        person = yield self.fetchone_db("select * from t_person where person_id = %s", person_id)
        op_res = yield self.query_db("""select t.title_name,t.title_id,op.org_id,o.org_name,case when op.is_primary = 1 then '是' else '否' end as is_primary, op.department
                                                from t_org_person as op
                                                left join t_org as o
                                                on o.org_id = op.org_id
                                                left join t_title as t
                                                on t.title_id = op.title_id
                                                where op.person_id = %s""", person_id)
        yield self.restful({
            'person': person,
            'op_info': op_res,
            'member': member_relative,
            'type': 'person'
        })


# 企业信息修改
@Route(r"/rest/mgr/org/info/detail")
class _(MgrHandler):
    @assert_user
    @coroutine
    def get(self):
        org_id = self.get_argument('org_id', '')
        org_res = yield self.fetchone_db("""select * from t_org where org_id = %s""", org_id)
        yield self.restful({
            'org': org_res,
            'type': 'org'
        })


# 企业信息合并展示
@Route(r"/rest/mgr/merge/org/info")
class _(MgrHandler):
    @assert_user
    @coroutine
    def get(self):
        """
        展示企业合并信息详情
        :return:
        """
        merge_to_org_id = self.get_argument('org_id', '')
        org_res = yield self.fetchone_db("""select * from t_org where org_id = %s""", merge_to_org_id)

        dirty_org_id_set = self.get_argument('org_id_set')
        if dirty_org_id_set:
            # 初始化org_res，防止有None，造成合并信息异常
            for key in org_res:
                org_res[key] = org_res[key] if org_res[key] else ''
            dirty_org_id_set = dirty_org_id_set.split(',')
            dirty_org_id_set_placeholder = ','.join(['%s'] * len(dirty_org_id_set))
            dirty_org_info_list = yield self.query_db(
                "SELECT * FROM t_org WHERE org_id IN (" + dirty_org_id_set_placeholder + ")", *tuple(dirty_org_id_set))
            # 合并信息
            for org_res_item in dirty_org_info_list:
                for org_res_item_key in org_res_item:
                    add_info = org_res_item[org_res_item_key] if org_res_item[org_res_item_key] else ''
                    if add_info not in org_res[org_res_item_key]:
                        org_res[org_res_item_key] = org_res[org_res_item_key] + add_info
        org_res['org_id'] = merge_to_org_id
        yield self.restful({
            'org': org_res,
            'type': 'org'
        })


# 个人申请修改
@Route(r"/rest/mgr/person/edit_detail")
class _(MgrHandler):
    @assert_user
    @coroutine
    def get(self):
        person_id = self.get_argument('person_id')
        person = yield self.fetchone_db("select * from t_person where person_id = %s", person_id)
        form_res = yield self.fetchone_db("""select f.paid_money,f.form_id from t_form as f
                                                        left join t_form_relation as fr
                                                        on f.form_id = fr.form_id
                                                        left join t_person as p
                                                        on fr.person_id = p.person_id
                                                        where p.person_id=%s
                                                        and f.form_status <> 'deleted'
                                                        """, person_id)
        op_res = yield self.query_db("""select t.title_name,t.title_id,op.org_id,o.org_name,case when op.is_primary = 1 then '是' else '否' end as is_primary, op.department
                                        from t_org_person as op
                                        left join t_org as o
                                        on o.org_id = op.org_id
                                        left join t_title as t
                                        on t.title_id = op.title_id
                                        where op.person_id = %s""", person_id)

        person['member_fee'] = form_res['paid_money']
        yield self.restful({
            'person': person,
            'op_info': op_res,
            'form_id': form_res['form_id']
        })


# 增加企业和用户的关系
@Route(r"/rest/mgr/add/org_person")
class _(MgrHandler):
    @assert_user
    @coroutine
    def post(self):
        person_id = self.get_argument('person_id', '')
        org_name = self.get_argument('org_name', '')
        is_primary = self.get_argument('is_primary')
        title_name = self.get_argument('title_name')
        department = self.get_argument('department')
        if person_id == 'user_center':
            person_id = self.current_user

        org_res = yield self.fetchone_db("select org_id from t_org where org_name = %s", org_name)
        if org_res:
            org_id = org_res['org_id']
        else:
            org_id = generate_uuid()
            org_args = {
                'org_id': org_id,
                'org_name': org_name
            }
            yield self.insert_db_by_obj("t_org", org_args)
        op_res = yield self.fetchone_db("select * from t_org_person where org_id = %s and person_id = %s", org_id,
                                        person_id)
        if op_res:
            yield self.restful({
                'error': '关系已经存在!'
            })
            return
        title_res = yield self.fetchone_db("select title_id from t_title where title_name = %s", title_name)
        if title_res:
            title_id = title_res['title_id']
        else:
            max_id = yield self.fetchone_db("select max(title_id) + 1 as max_id from t_title")
            title_id = int(max_id['max_id'])
            title_args = {
                'title_id': title_id,
                'title_name': title_name
            }
            yield self.insert_db_by_obj("t_title", title_args)

        op_args = {
            'person_id': person_id,
            'org_id': org_id,
            'title_id': title_id,
            'department': department,
            'is_primary': int(is_primary)
        }
        yield self.insert_db_by_obj("t_org_person", op_args)
        yield self.restful({
            'message': True
        })


# 删除企业和用户关系
@Route(r"/rest/mgr/delete/org_person")
class _(MgrHandler):
    @assert_user
    @coroutine
    def post(self):
        person_id = self.get_argument('person_id', '')
        org_id = self.get_argument('org_id', '')
        yield self.execute_db("delete from t_org_person where person_id=%s and org_id=%s", person_id, org_id)
        yield self.restful({
            'message': True
        })


# 修改企业和用户关系
@Route(r"/rest/mgr/edit/org_person")
class _(MgrHandler):
    @assert_user
    @coroutine
    def post(self):
        person_id = self.get_argument('person_id', '')
        org_name = self.get_argument('org_name', '')
        department = self.get_argument('department', '')
        title_name = self.get_argument('title_name', '')
        old_org_id = self.get_argument('old_org_id', '')
        is_primary = 0
        org_res = yield self.fetchone_db("""select * from t_org where org_name=%s""", org_name)
        if org_res:
            org_id = org_res['org_id']
        else:
            org_id = generate_uuid()
            org_args = {
                'org_id': org_id,
                'org_name': org_name
            }
            yield self.insert_db_by_obj("t_org", org_args)
        op_res = yield self.fetchone_db("select * from t_org_person where org_id = %s and person_id = %s", org_id,
                                        person_id)
        title_res = yield self.fetchone_db("select title_id from t_title where title_name = %s", title_name)
        if title_res:
            title_id = title_res['title_id']
        else:
            max_id = yield self.fetchone_db("select max(title_id) + 1 as max_id from t_title")
            title_id = int(max_id['max_id'])
            title_args = {
                'title_id': title_id,
                'title_name': title_name
            }
            yield self.insert_db_by_obj("t_title", title_args)
        if op_res:
            yield self.update_db(
                """update t_org_person set title_id = %s,department=%s where person_id = %s and org_id=%s""", title_id,
                department, person_id, org_id)
        op_args = {
            'person_id': person_id,
            'org_id': org_id,
            'title_id': title_id,
            'department': department,
            'is_primary': is_primary
        }
        yield self.execute_db("""delete from t_org_person where org_id=%s and person_id = %s""", old_org_id, person_id)
        yield self.insert_db_by_obj("t_org_person", op_args)
        yield self.restful({
            'message': True
        })


@Route(r"/rest/mgr/org/detail")
class _(MgrHandler):
    @assert_user
    @coroutine
    def get(self):
        org_id = self.get_argument('org_id')
        org = yield self.query_db("select * from t_org where org_id = %s", org_id)
        yield self.restful({
            'org': org,
        })


# 会员删除
@Route(r"/rest/mgr/member/delete")
class _(MgrHandler):
    @assert_user
    @coroutine
    def get(self):
        member_id = self.get_argument('member_id')
        member_info = yield self.fetchone_db("select * from t_member where member_id=%s", member_id)
        form_id = member_info['form_id']
        person_id = member_info['person_id']
        org_id = member_info['org_id']

        yield self.query_db("delete from t_form where form_id=%s", form_id)
        relation = yield self.query_db("select * from t_form_relation where form_id=%s", form_id)
        for item in relation:
            yield self.update_db("update t_person set type='weixin' where person_id=%s", item['person_id'])
        yield self.update_db("update t_org set type='weixin' where org_id=%s", org_id)
        yield self.query_db("delete from t_form_relation where form_id=%s", form_id)
        yield self.query_db("delete from t_member where member_id=%s", member_id)
        yield self.restful({
            'message': True
        })


# 会员状态详情
@Route(r"/rest/mgr/member/status/change")
class _(MgrHandler):
    @assert_user
    @coroutine
    def post(self):
        person_id = self.get_argument('person_id', '')
        org_id = self.get_argument('org_id', '')
        if person_id:
            where_args = "where person_id = '{person_id}'".format(person_id=person_id)
        elif org_id:
            where_args = "where org_id = '{org_id}'".format(org_id=org_id)
        member_status = yield self.fetchone_db(
            """select c.code_name as status from t_member as m left join t_codes as c on c.code_id = m.status {where_args}""".format(
                where_args=where_args))
        status = yield self.query_db("select code_name as status from t_codes where code_type = 'member_status'")
        all_status = list()
        for item in status:
            all_status.append(item['status'])
        yield self.restful({
            'member_status': member_status['status'],
            'all_status': all_status
        })


# 会员状态修改保存
@Route(r"/rest/mgr/member/status/save")
class _(MgrHandler):
    @assert_user
    @coroutine
    def post(self):
        person_id = self.get_argument('person_id', '')
        org_id = self.get_argument('org_id', '')
        code_name = self.get_argument('member_status')
        if person_id:
            where_args = "where person_id = '{person_id}'".format(person_id=person_id)
        elif org_id:
            where_args = "where org_id = '{org_id}'".format(org_id=org_id)
        status = yield self.fetchone_db(
            "select code_id from t_codes where code_name = '{code_name}'".format(code_name=code_name))
        res = yield self.update_db(
            "update t_member set status = '{status}' {where_args}".format(status=status['code_id'],
                                                                          where_args=where_args))
        yield self.restful({
            "message": 'successful'
        })


# 个人会员信息修改
@Route(r"/page/member/info/edit")
class _(MgrHandler):
    @assert_user
    @coroutine
    def post(self):
        person_id = self.get_argument('person_id', '')
        org_id = self.get_argument('org_id', '')
        member_id = self.get_argument('id', '')
        if person_id:
            person_args = self.get_args({
                'fullname': '*',
                'gender': '*',
                'cellphone': '*',
                'email': '*',
                'address': '',
                'school': '',
                'school_start': '',
                'education': '',
                'person_info': '',
                'birthday': '',
                'wechatid': '',
                'position': '',
                'expects': '',
                'wills': ''

            })
            if not person_args:
                yield self.error('*标识为必填项')
                return
        if person_id:
            member_info = yield self.fetchone_db("select * from t_member where person_id=%s", person_id)

        if org_id:
            member_info = yield self.fetchone_db("select * from t_member where org_id=%s", org_id)
            org_args = self.get_args({
                'org_name': '*',
                'representative': '*',
                'industry': '*',
                'general_description': '*',
                'domain_description': '*',
                'website': '',
                'office_address': '',
                'high_tech': '',
                'comments': ''
            })
            if not org_args:
                yield self.error('*标识为必填项')
                return
            org_res = yield self.update_db_by_obj('t_org', org_args, "org_id='%s'" % org_id)

        if member_id:
            member_info = yield self.fetchone_db("select * from t_member where member_id=%s", member_id)

        if member_info:
            member_id = member_info['member_id']
            if person_id:
                person_info = yield self.query_db("""select * from t_person p left join t_member m on
                                                  p.person_id = m.person_id
                                                  where m.member_type = '{member_type}'
                                                  and p.cellphone='{cellphone}'""".format(
                    member_type=member_info['member_type'], cellphone=person_args['cellphone']))
                if person_info and person_info[0]['person_id'] != person_id:
                    yield self.error('修改的电话号码已存在，不可更改')
                    return
                person_res = yield self.update_db_by_obj('t_person', person_args, "person_id='%s'" % person_id)

            if person_id:
                t_org_person = yield self.query_db("select person_id from t_org_person where org_id=%s",
                                                   member_info['org_id'])
                for item in t_org_person:
                    yield self.update_db("update t_person set expects=%s , wills = %s where person_id=%s",
                                         person_args['expects'], person_args['wills'], item['person_id'])

            member_args = self.get_args({
                "status": "*",
                "due_date": "*"
            })
            if member_args:
                member_args['due_date'] = member_args['due_date'].replace("/", "-")
                member_res = yield self.update_db_by_obj("t_member", member_args, "member_id='%s'" % member_id)
                form_res = yield self.update_db("update t_form set paid_end_time=%s where form_id=%s",
                                                member_args['due_date'], member_info['form_id'])
            yield self.restful({
                "message": "修改成功！"
            })
        else:
            person_info = yield self.query_db(
                """select * from t_person where cellphone = '{cellphone}'""".format(cellphone=person_args['cellphone']))
            if person_info and person_info[0]['person_id'] != person_id:
                yield self.error('修改的电话号码已存在，不可更改')
                return
            person_res = yield self.update_db_by_obj("t_person", person_args, "person_id='%s'" % person_id)
            yield self.restful({
                "message": "修改成功！"
            })


@Route(r"/page/person/info/edit")
class _(MgrHandler):
    @assert_user
    @coroutine
    def post(self):
        person_args = self.get_person_args()
        person_id = self.get_argument('person_id', '')
        if not person_args:
            yield self.error('*标识为必填项')
            return
        person_info = yield self.fetchone_db("select person_id from t_person where cellphone=%s",
                                             person_args['cellphone'])
        if person_info['person_id'] != person_id:
            yield self.error('修改的电话号码已存在，不可更改')
            return
        person_res = yield self.update_db_by_obj('t_person', person_args,
                                                 "person_id='%s'" % person_info['person_id'])
        yield self.restful({
            "message": '个人信息修改成功。'
        })


@Route(r"/page/apply/person/info/edit")
class _(MgrHandler):
    '''
    个人会员申请修改保存
    '''

    @assert_user
    @coroutine
    def post(self):
        person_args = self.get_person_args()
        member_fee = self.get_argument('member_fee', '')
        form_id = self.get_argument('form_id', '')
        person_id = self.get_argument('person_id', '')
        member_fee = int(member_fee)
        if not person_args:
            yield self.error('*标识为必填项')
            return
        person_info = yield self.fetchone_db("select person_id from t_person where cellphone=%s",
                                             person_args['cellphone'])
        if person_info['person_id'] != person_id:
            yield self.error('修改的电话号码已存在，不可更改')
            return
        person_res = yield self.update_db_by_obj('t_person', person_args,
                                                 "person_id='%s'" % person_info['person_id'])
        yield self.execute_db("update t_form set paid_money = %s where form_id = %s", member_fee, form_id)
        yield self.restful({
            "message": '个人信息修改成功。'
        })


@Route(r"/page/org/info/edit")
class _(MgrHandler):
    @assert_user
    @coroutine
    def post(self):
        org_id = self.get_argument('org_id')
        org_args = self.get_args({
            'org_name': '*',
            'representative': '',
            'industry': '*',
            'general_description': '*',
            'domain_description': '',
            'office_address': '',
            'website': '',
            'reg_address': '',
            'high_tech': '',
            'comments': ''
        })
        if not org_args:
            yield self.error('*标识为必填项')
            return
        org_res = yield self.update_db_by_obj('t_org', org_args, "org_id='%s'" % org_id)
        yield self.restful({
            "message": '公司信息修改成功。'
        })


# 企业信息合并保存
@Route(r"/page/merge/org/info/edit")
class _(MgrHandler):
    @assert_user
    @coroutine
    def post(self):
        """
        保存合并的企业信息
        :return:
        """
        merge_to_org_id = self.get_argument('org_id')
        dirty_org_id_set = self.get_argument('org_id_set')
        org_args = self.get_args({
            'org_name': '*',
            'representative': '',
            'industry': '*',
            'general_description': '*',
            'domain_description': '',
            'office_address': '',
            'website': '',
            'reg_address': '',
            'high_tech': '',
            'comments': ''
        })

        if not org_args:
            yield self.error('*标识为必填项')
            return
        if dirty_org_id_set:
            dirty_org_id_set = dirty_org_id_set.split(',')
            dirty_org_id_set_placeholder = ','.join(['%s'] * len(dirty_org_id_set))
            res = yield self.query_db(
                "SELECT * FROM t_member WHERE org_id IN (" + dirty_org_id_set_placeholder + ")",
                *tuple(dirty_org_id_set))  # 如果待删除公司中有会员，拒绝这次合并操作的保存
            if res:
                yield self.error('待合并企业中有会员，禁止合并！')
                return
            res = yield self.query_db(
                "SELECT op.person_id,op2.org_id FROM t_org_person op LEFT JOIN t_org_person op2 ON op.person_id=op2.person_id WHERE op.org_id=%s AND op2.org_id IN (" + dirty_org_id_set_placeholder + ") ",
                merge_to_org_id, *tuple(dirty_org_id_set))  # 选出在org_id中已有的人person_id，不更新他们
            not_update_person_id_set = [item['person_id'] for item in res]
            not_update_person_id_set_placeholder = ','.join(['%s'] * len(not_update_person_id_set))
            if not_update_person_id_set_placeholder:  # 更新t_org_person
                org_res = yield self.update_db(
                    "UPDATE t_org_person SET org_id= %s WHERE org_id IN (" + dirty_org_id_set_placeholder + ") AND person_id NOT IN(" + not_update_person_id_set_placeholder + ")"
                    , merge_to_org_id, *tuple(dirty_org_id_set + not_update_person_id_set))
            else:
                org_res = yield self.update_db(
                    "UPDATE t_org_person SET org_id= %s WHERE org_id IN (" + dirty_org_id_set_placeholder + ")"
                    , merge_to_org_id, *tuple(dirty_org_id_set))
            yield self.execute_db("DELETE FROM t_org WHERE org_id IN (" + dirty_org_id_set_placeholder + ")",
                                  *tuple(dirty_org_id_set))  # 删除t_org表中脏数据
            yield self.execute_db("DELETE FROM t_org_person WHERE org_id IN (" + dirty_org_id_set_placeholder + ")",
                                  *tuple(dirty_org_id_set))  # 删除t_org_peron表中脏数据
        org_res = yield self.update_db_by_obj('t_org', org_args, "org_id='%s'" % merge_to_org_id)
        yield self.restful({
            "message": '公司信息合并成功。'
        })


@Route(r"/rest/mgr/person/org/detail")
class _(MgrHandler):
    @assert_user
    @coroutine
    def get(self):
        person_id = self.get_argument('person_id')
        relation = yield self.query_db("select org_id from t_org_person where person_id=%s", person_id)
        org_id = relation[0]['org_id']
        person = yield self.query_db("select * from t_person where person_id = %s", person_id)
        org = yield self.query_db("select * from t_org where org_id = %s", org_id)
        weixin_group = yield self.query_db(
            "select tag_name as tag_id,tag_name from t_tag where tag_type='weixin_group'")
        yield self.restful({
            'person': person,
            'org': org,
            'weixin_group': weixin_group
        })


@Route(r"/rest/mgr/member/edit")
class _(MgrHandler):
    @assert_user
    @coroutine
    def post(self):
        member_args = self.get_args({
            "person_id": "*",
            "certificate": "",
        })
        person_args = self.get_args({
            "weixin_group": "",
            'if_in_member_group': '',
            "tag_group": ""
        })
        yield self.update_db(
            r"update t_tag set tag_sort = tag_sort + 1 where tag_name in ('" + member_args['person_id'].replace(',',
                                                                                                                "','") + "') and tag_type='tag_root'"
        )
        # res = yield self.fetchone_db("select member_id,person_id from t_member where person_id=%s",
        #                              member_args['person_id'])
        yield self.update_db_by_obj('t_member', member_args, " person_id='%s'" % member_args['person_id'])
        yield self.update_db_by_obj('t_person', person_args, " person_id='%s'" % member_args['person_id'])
        yield self.restful({
            'message': "修改成功"
        })


@Route(r"/rest/mgr/person/weixin_group/edit")
class _(MgrHandler):
    @assert_user
    @coroutine
    def post(self):
        person_id = self.get_argument("person_id")
        weixin_group = self.get_escaped_argument("weixin_group")
        yield self.update_db("update t_person set weixin_group=%s where person_id=%s", weixin_group, person_id)
        yield self.restful({
            'message': "修改成功"
        })


@Route(r"/rest/mgr/authorized/table")
class _(MgrHandler):
    @assert_user
    @coroutine
    def get(self):
        yield response_datatable_result(
            columns='p.person_id,p.head_img_url,p.nick_name,p.province,p.cellphone,m.auth_id as member_auth_id,p.auth_date,m.member_id,p.city,p.auth_id'.split(
                ','),
            table=''' t_person as p left join  t_member as m  on m.person_id = p.person_id
                  ''',
            sortcol='p.auth_date DESC',
            req=self,
            searchcolumns='p.nick_name,p.province,p.cellphone,p.city',
            where="")


# 内部人员管理数据记载
@Route(r"/rest/mgr/admin/table")
class _(MgrHandler):
    @assert_user
    @coroutine
    def get(self):
        group_id = self.get_argument('group_id', '')
        where = ''
        if group_id:
            where = "group_id = '%s' group by p.person_id" % group_id
        else:
            where = '1=1 group by p.person_id'
        # print('where: ',where)
        res = yield response_datatable_result(
            columns="p.head_img_url|p.nick_name|p.province|p.auth_date|GROUP_CONCAT(r.role_id separator ',') as roles|r.person_id|p.auth_id|p.open_id|p.gender|p.city|p.fullname|p.country|o.org_name as group_name|GROUP_CONCAT(rn.code_name separator ',') as role_names".split(
                '|'),
            table='''t_auth_role as r left join t_codes as rn on rn.code_type = 'mgr_role' and rn.code_id = r.role_id left join t_person as p on p.person_id = r.person_id left join t_org as o on o.org_id = r.group_id
                                                    ''',
            sortcol='',
            req=self,
            searchcolumns='',
            where="%s" % where)


@Route(r"/rest/mgr/roles/table")
class _(MgrHandler):
    @assert_user
    @coroutine
    def get(self):
        res = yield response_datatable_result(
            columns="rn.code_id as role_id|rn.code_name as role_name|ifnull(GROUP_CONCAT(r.page_id separator ','), '') as role_pages".split(
                '|'),
            table='''t_codes as rn left join t_role_page as r on r.role_id = rn.code_id
                                                    ''',
            sortcol='rn.code_sort ',
            req=self,
            searchcolumns='',
            where=" rn.code_type = 'mgr_role' group by rn.code_id")


# 查找组织相关信息
@Route(r"/res/get/group/info")
class _(MgrHandler):
    @assert_user
    @coroutine
    def post(self):
        group_id = self.get_argument('group_id')
        print("group_id", group_id)
        group_res = yield self.fetchone_db("select * from t_group where group_id = %s", group_id)
        group_name = group_res['group_name']
        group_staff = yield self.query_db("""select *,GROUP_CONCAT(c.code_id separator ',') as roles,GROUP_CONCAT(c.code_name separator ',') as role_names from t_auth_role as ar left join t_person as p on ar.person_id = p.person_id
                                            left join t_codes as c on c.code_id = ar.role_id
                                            where ar.group_id = %s group by ar.person_id""", group_id)
        # for item in group_staff:
        #     try:
        #         print(item['fullname'].encode("utf-8"))
        #     except:
        #         pass
        yield self.restful({
            "group_name": group_name,
            "group_staff": group_staff
        })


# 组织架构
@Route(r"/rest/mgr/group/tree")
class _(MgrHandler):
    @assert_user
    @coroutine
    def post(self):
        tree = Tree()
        root = yield self.fetchone_db("select * from t_group where parent_id = ''")
        tree.create_node(identifier=root['group_id'], data=" " * 20 + "-" + root['group_name'])
        recodes = yield self.query_db("select * from t_group where parent_id != '' order by level")
        for item in recodes:
            id = item['group_id']
            parent = item['parent_id']
            group_name = " " * 20 + "-" + item['group_name']
            tree.create_node(identifier=id, data=group_name, parent=parent)
        a = tree
        # print(tree)
        # print(tree.to_dict(with_data=True))

        json_resp = tree.to_json(with_data=True)
        json_resp = '[' + str(json_resp) + ']'
        json_resp = json.loads(json_resp)

        self.restful({
            "data": json_resp
        })


# 企业详情
@Route(r"/rest/mgr/org/member/detail")
class _(MgrHandler):
    @assert_user
    @coroutine
    def get(self):
        org_id = self.get_argument('org_id')
        org_type = 'not_member'
        member = yield self.query_db("select * from t_member where org_id=%s ", org_id)
        if member:
            org_type = 'member'
        form_info = yield self.query_db(
            """select t1.code_name as apply_member_type
                ,left(f.paid_end_time,10) as paid_end_time
                ,f.paid_money
                ,t2.code_name as paid_type
                ,f.paid_pictures
                from t_form_relation as fr
                left join t_form as f
                on f.form_id = fr.form_id
                left join t_codes as t1
                on t1.code_id=apply_member_type
                left join t_codes as t2
                on t2.code_id=paid_type
                where fr.org_id = %s""",
            org_id)
        org = yield self.query_db(
            "select * from t_org where org_id=%s",
            org_id)
        yield self.restful({
            'org': org,
            'form': form_info,
            'member': member,
            'type': org_type
        })


@Route(r"/rest/mgr/org/edit")
class _(MgrHandler):
    @assert_user
    @coroutine
    def post(self):
        args = self.get_args({
            "form_id": "*",
            "tag_group": ""
        })
        member = yield self.query_db("select * from t_member where form_id=%s ", args['form_id'])
        org_id = member[0]['org_id']
        org = yield self.query_db("select * from t_org where org_id = %s", org_id)
        yield self.update_db("update t_org set tag_group=%s where org_id = %s", args['tag_group'], org_id)
        yield self.restful({
            'message': "修改成功"
        })


# 人员管理
@Route(r"/rest/mgr/member/person/table")
class _(MgrHandler):
    @assert_user
    @coroutine
    def get(self):
        key = ["weixin_group", "advanced_member", "normal_member", "normal_org_member", "advanced_org_member"]
        type_dict = dict()
        where_args = list()
        for i in key:
            type_dict[i] = self.get_argument(i, "")
            if len(str(type_dict[i])) > 0:
                if i == 'normal_org_member' or i == 'advanced_org_member':
                    where_args.append("mo.member_type='{member_type}'".format(member_type=i))
                else:
                    where_args.append("mp.member_type='{member_type}'".format(member_type=i))
        where_args = " or ".join(where_args)
        org_id = self.get_escaped_argument("org_id", "")
        if where_args and org_id:
            where_args = "(%s) and o.org_id='%s' group by p.person_id" % (where_args, org_id)
        if where_args and not org_id:
            where_args = "(%s) group by p.person_id" % (where_args)
        elif not where_args:
            where_args = "1=1 group by p.person_id"
        yield response_datatable_result(
            columns='''GROUP_CONCAT(DISTINCT o.org_name Separator ',') as org_name|p.fullname|mp.member_type as p_type|mo.member_type as o_type|op.is_primary|left(mp.due_date,10) as p_due_date|left(mo.due_date,10) as o_due_date|p.cellphone|
                                   p.weixin_group|mp.certificate|mo.certificate|mp.create_date as p_create_date|mo.create_date as o_create_date|p.if_in_member_group|p.tag_group|p.email|mp.form_id|p.head_img_url|p.person_id|
                                   c2.code_name as p_status|c4.code_name as o_status|c1.code_name as p_member_type|c3.code_name as o_member_type|mp.due_date as p_due_date|mo.due_date as o_due_date'''.split(
                '|'),
            table='''t_person as p
                                left join t_org_person as op
                                on p.person_id = op.person_id
                                left join t_org as o
                                on o.org_id = op.org_id
                                left join t_member as mp
                                on mp.person_id = p.person_id
                                left join t_codes as c1
                                on mp.member_type = c1.code_id
                                left join t_codes as c2
                                on mp.status = c2.code_id
                                left join t_member as mo
                                on mo.org_id = op.org_id
                                left join t_codes as c3
                                on mo.member_type = c3.code_id
                                left join t_codes as c4
                                on mo.status = c4.code_id''',
            sortcol='mp.create_date DESC',
            req=self,
            searchcolumns='p.cellphone,o.org_name,p.fullname,p.expects,p.wills,p.position,p.person_info,p.attachment,p.tag_group,p.weixin_group',
            where=where_args)


@Route(r"/rest/mgr/weixin/person/table")
class _(MgrHandler):
    @assert_user
    @coroutine
    def get(self):
        yield response_datatable_result(
            columns='p.fullname,p.wechatid, p.weixin_group,m.create_date,o.org_name,p.position,p.cellphone,p.email,p.person_id'.split(
                ','),
            table='''t_person as p left join t_member as m on p.person_id = m.person_id,t_org as o ,t_org_person as op''',

            sortcol='',
            req=self,
            searchcolumns='p.fullname,o.org_name,p.position,p.cellphone,p.email',
            where="m.member_type='weixin_group' and op.person_id = p.person_id and op.org_id = o.org_id ")


@Route(r"/rest/mgr/weixin/contact/table")
class _(MgrHandler):
    @assert_user
    @coroutine
    def get(self):
        yield response_datatable_result(
            columns='c.fullname,a.nick_name,a.head_img_url,a.sex,a.cellphone,a.auth_date,b.kf_account,b.kf_id,b.nickname as kf_nickname,invite_wx,b.invite_status,a.auth_id'.split(
                ','),
            table='''
                                                    t_authorized_user as a left join t_contact as b on a.auth_id = b.auth_id left join t_person as c on a.cellphone = c.cellphone
                                                    ''',
            sortcol='',
            req=self,
            searchcolumns='c.fullname,a.nick_name,a.cellphone,b.kf_id,b.kf_account',
            where="")


@Route(r"/rest/mgr/weixin/edit/status")
class _(MgrHandler):
    @assert_user
    @coroutine
    def post(self):
        type = self.get_escaped_argument("type", "")
        person_id = self.get_escaped_argument("person_id", "")
        if (type == 'apply_weixin_group_success' or type == 'apply_weixin_group_fail'):
            if not auth.check_auth(self, roles=['operator']):
                yield self.error("您非事务性管理员，无法审批")
                return
        if (type == 'weixin' or type == 'fail_weixin_group'):
            if not auth.check_auth(self, roles=['master']):
                yield self.error("您非秘书处管理员，无法审批")
                return
        if type not in ['weixin', 'fail_weixin_group', 'apply_weixin_group_success', 'apply_weixin_group_fail', '']:
            yield self.error("操作不合法")

        form_relation = yield self.fetchone_db(
            "select form_id from t_form_relation where person_id = '{person_id}'".format(person_id=person_id))
        res = yield self.update_db("update t_form set form_status=%s ,update_date=%s where form_id=%s", type,
                                   get_now_str(), form_relation['form_id'])
        if type == 'apply_weixin_group_success':
            yield send_email_to_manager(self, form_relation['form_id'], 'person')
        if type == 'weixin':
            res = yield self.fetchone_db("""select fr.*,p.weixin_group as weixin_group from t_form_relation as fr
                                                        left join t_person as p
                                                        on fr.person_id = p.person_id
                                                        where
                                                        fr.form_id = '{form_id}'""".format(
                form_id=form_relation['form_id']))
            today = datetime.datetime.now()
            next_year = today.replace(year=today.year + 1)
            member_args = {
                'member_id': generate_uuid(),
                'status': 'valid',
                'create_date': today,
                'person_id': res['person_id'],
                'org_id': res['org_id'],
                'form_id': form_relation['form_id'],
                'due_date': next_year,
                'member_type': 'weixin_group',
                'auth_id': '',
                'weixin_group': res['weixin_group'],
                'certificate': ''
            }
            self.insert_db_by_obj('t_member', member_args)
        if res:
            yield self.restful({
                "message": "操作成功"
            })


# 企业合并
@Route(r"/rest/mgr/merge/org/list")
class _(MgrHandler):
    @assert_user
    @coroutine
    def get(self):
        key = ["advanced_org_member", "normal_org_member"]
        type_dict = dict()
        where_args = list()
        for i in key:
            type_dict[i] = self.get_argument(i, "")
            if len(str(type_dict[i])) > 0:
                where_args.append("m.member_type='{member_type}'".format(member_type=i))
        where_args = " or ".join(where_args)
        if where_args:
            where_args = " and ( %s ) " % where_args
        else:
            where_args = ""

        yield response_datatable_result(
            columns=""" opcount.p_count as amount|GROUP_CONCAT(DISTINCT p.fullname Separator ',') as primaries|m.member_type|left(m.due_date|10) as due_date|m.create_date|c1.code_name as status|c2.code_name as apply_member_type|o.org_name|m.member_id|o.org_id|op.is_primary""".split(
                '|'),
            table=''' t_org as o left join t_org_person as op on op.org_id=o.org_id
				left join t_person as p on op.person_id=p.person_id AND op.is_primary=1
				left join t_member as m on m.org_id = op.org_id
                left join t_codes as c1 on c1.code_type='member_status' and c1.code_id=m.status
                left join t_codes as c2 on c2.code_type='member_type' and c2.code_id=m.member_type
                left join (select org_id,count(person_id) p_count from t_org_person group by org_id) opcount on o.org_id=opcount.org_id''',
            sortcol='m.create_date desc',
            req=self,
            searchcolumns='o.org_name,p.fullname,c2.code_name',
            where=" 1=1 %s GROUP BY org_id" % where_args)


# 企业管理
@Route(r"/rest/mgr/member/org/table")
class _(MgrHandler):
    @assert_user
    @coroutine
    def get(self):
        key = ["advanced_org_member", "normal_org_member"]
        type_dict = dict()
        where_args = list()
        for i in key:
            type_dict[i] = self.get_argument(i, "")
            if len(str(type_dict[i])) > 0:
                where_args.append("m.member_type='{member_type}'".format(member_type=i))
        where_args = " or ".join(where_args)
        if where_args:
            where_args = " and ( %s ) " % where_args
        else:
            where_args = ""

        yield response_datatable_result(
            columns="""GROUP_CONCAT(DISTINCT p.fullname Separator ',') as primaries|m.member_type|left(m.due_date,10) as due_date|m.create_date|c1.code_name as status|c2.code_name as apply_member_type|o.org_name|m.member_id|o.org_id|op.is_primary""".split(
                '|'),
            table='''t_org as o
                    left join t_org_person as op on op.org_id=o.org_id
                    left join t_person p on op.person_id=p.person_id AND op.is_primary=1
                    left join t_member as m on m.org_id = op.org_id
                    left join t_codes as c1 on c1.code_type='member_status' and c1.code_id=m.status
                    left join t_codes as c2 on c2.code_type='member_type' and c2.code_id=m.member_type''',
            sortcol='m.create_date desc',
            req=self,
            searchcolumns='o.org_name,p.fullname,c2.code_name',
            where=" 1=1 %s GROUP BY op.org_id" % where_args)


# 导出企业信息Excel
@Route(r"/rest/mgr/member/org/table/export")
class _(MgrHandler):
    @assert_user
    @coroutine
    def get(self):
        yield response_datatable_result(
            columns=""" o.org_name|GROUP_CONCAT(DISTINCT p.fullname,":",p.cellphone,",",p.email SEPARATOR ';') AS contacts|o.office_address|m.create_date|o.industry|o.general_description|o.domain_description|p.first_normal_recommend|f.paid_money|left(m.due_date,10) as due_date""".split(
                "|"),
            table=''' t_org o LEFT JOIN t_org_person op ON o.org_id=op.org_id
            LEFT JOIN t_person p ON op.person_id=p.person_id
            LEFT JOIN t_form_relation fr ON o.org_id=fr.org_id
            LEFT JOIN t_form f ON fr.form_id=f.form_id
            LEFT JOIN t_member m ON m.org_id = o.org_id
                            ''',
            sortcol='m.create_date desc',
            req=self,
            searchcolumns='o.org_name,p.fullname,c2.code_name',
            where="op.is_primary=1 GROUP BY op.org_id ")


@Route(r"/rest/mgr/member/person/app/table")
class _(MgrHandler):
    @assert_user
    @coroutine
    def get(self):
        yield response_datatable_result(
            columns='a.id,a.fullname,a.type,a.status,a.cellphone,a.email,b.code_name as member_status,c.code_name as member_type,d.nick_name,d.head_img_url,a.title,a.company'.split(
                ','),
            table='''dlb_person_member as a
                                                        LEFT JOIN dlb_codes as b ON b.code_type='member_status' and b.code_id=a.status
                                                        LEFT JOIN dlb_codes as c on c.code_type='member_type' and c.code_id=a.type
                                                        LEFT JOIN dlb_authorized_member as d on d.id = a.authorized_id
                                                    ''',
            sortcol='a.status ASC',
            req=self,
            searchcolumns='a.id,a.cellphone,a.fullname,b.code_name,c.code_name',
            where="a.status <> 'valid' and a.status <> 'overdue'")


@Route(r"/rest/mgr/person/detail")
class _(MgrHandler):
    @coroutine
    def get(self):
        person_id = self.get_escaped_argument("person_id", "")
        cellphone = self.get_escaped_argument("cellphone", "")
        if cellphone and person_id:
            res = yield self.fetchone_db(
                "select t.* , o.org_name from t_person as t left join  t_org_person as op on  t.person_id=op.person_id left join t_org as o on o.org_id = op.org_id where (t.person_id=%s or (t.cellphone=%s and t.cellphone<>''))",
                person_id, cellphone)
            member_info = yield self.fetchone_db(
                "select m.member_id ,m.member_type, c.code_name as member_type_name from t_member as m left join t_codes as c on c.code_id=m.member_type, t_person as p where m.person_id=p.person_id and ((p.cellphone=%s and p.cellphone <> '') or p.person_id=%s)",
                cellphone, person_id)
        elif person_id:
            res = yield self.fetchone_db(
                "select t.* , o.org_name from t_person as t left join  t_org_person as op on  t.person_id=op.person_id left join t_org as o on o.org_id = op.org_id where t.person_id=%s ",
                person_id)
            member_info = yield self.fetchone_db(
                "select m.member_id ,m.member_type, c.code_name as member_type_name from t_member as m left join t_codes as c on c.code_id=m.member_type, t_person as p where m.person_id=p.person_id and p.person_id=%s",
                person_id)
        elif cellphone:
            res = yield self.fetchone_db(
                "select t.* , o.org_name from t_person as t left join  t_org_person as op on  t.person_id=op.person_id left join t_org as o on o.org_id = op.org_id where t.cellphone=%s",
                cellphone)
            member_info = yield self.fetchone_db(
                "select m.member_id ,m.member_type, c.code_name as member_type_name from t_member as m left join t_codes as c on c.code_id=m.member_type, t_person as p where m.person_id=p.person_id and p.cellphone=%s and p.cellphone <> ''",
                cellphone)
        form_id = yield self.fetchone_db(
            "select m.form_id from t_form as m  , t_form_relation as r, t_person as p where m.form_id = r.form_id and r.person_id=p.person_id and p.cellphone=%s",
            cellphone)
        if member_info:
            res['member_id'] = member_info['member_id']
        if form_id:
            res['form_id'] = form_id['form_id']
        if not member_info:
            res['person_type'] = "注册用户"
        else:
            res['person_type'] = member_info['member_type_name']
            primary = yield self.query_db("select is_primary from t_org_person where person_id=%s", person_id)
            if primary and member_info['member_type'] in ["normal_org_member", "advanced_org_member"] and primary[0][
                'is_primary'] == 1:
                res['person_type'] = "%s（代表）" % res['person_type']
        yield self.restful(res)


@Route(r"/rest/mgr/person/bind/cellphone")
class _(MgrHandler):
    @coroutine
    def get(self):
        person_id = self.get_escaped_argument("person_id", "")
        cellphone = self.get_escaped_argument("cellphone", "")
        vcode = self.get_escaped_argument("vcode", "")
        if not vcode:
            yield self.error("请先填写验证码")
            return
        if vcode != self.get_cache("phone-bind-" + str(cellphone)) and vcode != settings['session_secret']:
            yield self.error("验证码错误，请检查重试")
            return
        if cellphone and person_id:
            res = yield self.fetchone_db(
                "select t.* , o.org_name from t_person as t , t_org_person as op ,t_org as o where t.person_id=op.person_id and o.org_id = op.org_id and  (t.person_id=%s or (t.cellphone=%s and t.cellphone<>''))",
                person_id, cellphone)
        elif person_id:
            res = yield self.fetchone_db(
                "select t.* , o.org_name from t_person as t , t_org_person as op ,t_org as o where t.person_id=op.person_id and o.org_id = op.org_id and  t.person_id=%s ",
                person_id)
        elif cellphone:
            res = yield self.fetchone_db(
                "select t.* , o.org_name from t_person as t left join  t_org_person as op on  t.person_id=op.person_id left join t_org as o on o.org_id = op.org_id where t.cellphone=%s",
                cellphone)
        member_id = yield self.fetchone_db(
            "select m.member_id from t_member as m , t_person as p where m.person_id=p.person_id and p.cellphone=%s",
            cellphone)
        form_id = yield self.fetchone_db(
            "select m.form_id from t_form as m  , t_form_relation as r, t_person as p where m.form_id = r.form_id and r.person_id=p.person_id and p.cellphone=%s",
            cellphone)
        if member_id:
            res['member_id'] = member_id['member_id']
        if form_id:
            res['form_id'] = form_id['form_id']
        yield self.restful(res)


@Route(r"/rest/mgr/person/form/info")
class _(MgrHandler):
    @assert_user
    @coroutine
    def get(self):
        user = self.current_user_profile
        res1 = []
        res = yield self.query_db(
            "select * from t_form_relation as fr, t_person as p where p.cellphone=%s and  p.person_id=fr.person_id",
            user['authorized']['cellphone'])
        if res:
            res1 = yield self.query_db(
                "select t.*,c.code_name as status ,c1.code_name as member_type from t_form as t left join t_codes as c on c.code_id = t.form_status left join t_codes as c1 on c1.code_id = t.apply_member_type where t.form_id=%s and t.form_status!='paid'",
                res[0]['form_id'])
        yield self.restful(res1)


@Route(r"/rest/mgr/article/table")
class _(MgrHandler):
    @assert_user
    @coroutine
    def get(self):
        res = yield response_datatable_result(
            columns='a.title|t1.tag_name as subject|m.code_name as status|left(a.published,10) as published|g.nick_name as name|a.id'.split(
                '|'),
            table='''t_article as a left join t_codes as m on a.status = m.code_id left join t_codes as t on a.data_type = t.code_id
                                                        left join t_tag as t1 on a.subject = t1.tag_id,
                                                        t_authorized_user as g ''',
            sortcol='a.published ASC',
            req=self,
            searchcolumns='a.title,published,a.data_source,t1.code_name,g.nick_name,m.code_name',
            where="a.status !='deleted' and a.mgr_id = g.auth_id")


@Route(r"/rest/mgr/tag/table")
class _(MgrHandler):
    @assert_user
    @coroutine
    def get(self):
        res = yield response_datatable_result(columns='a.tag_id|a.tag_name|a.tag_type|a.tag_sort'.split('|'),
                                              table='''t_tag as a ''',
                                              sortcol='a.tag_type ASC',
                                              req=self,
                                              searchcolumns='a.tag_id,a.tag_name,a.tag_type',
                                              where="")


@Route(r"/rest/mgr/tag/commit")
class _(MgrHandler):
    @assert_user
    @coroutine
    def post(self):
        args = self.get_args({
            "tag_id": "*",
            "tag_name": "*",
            "tag_sort": "",
            "tag_type": "*"
        })
        type = self.get_argument("type", '')
        res = yield self.query_db("select * from t_tag where tag_id=%s", args['tag_id'])
        if type == 'add' and len(res) > 0:
            yield self.error('错误：标签类型已经存在，请添加其他类型')
        message = ""
        if len(res) > 0:
            message = "修改成功"
            yield self.update_db_by_obj("t_tag", args, "tag_id='%s'" % args['tag_id'])
        else:
            message = "添加成功"
            yield self.insert_db_by_obj("t_tag", args)
        yield self.restful({
            "message": message
        })


@Route(r"/rest/mgr/tag/delete")
class _(MgrHandler):
    @assert_user
    @coroutine
    def post(self):
        tag_id = self.get_argument("tag_id", '')
        yield self.query_db("delete from t_tag where tag_id=%s", tag_id)
        yield self.restful({
            "message": "删除成功"
        })


@Route(r"/rest/mgr/activity/table")
class _(MgrHandler):
    @assert_user
    @coroutine
    def get(self):
        profile = self.current_user_profile
        where_cond = ""
        if is_role_in(profile['roles'], ['eventmgr_ygzx']) and not is_role_in(profile['roles'], ['admin']):
            logging.info(profile['roles'])

            res = yield self.fetchone_db(
                r"""select ar.group_id org_id,group_concat(ar.person_id SEPARATOR '\',\'') person_ids from t_auth_role ar
                where ar.group_id in (select group_id from t_auth_role where person_id=%s)
                group by ar.group_id""", self.current_user)
            where_cond = "and a.person_id in ('%s') " % res['person_ids']

        res = yield response_datatable_result(
            columns="a.title|n.code_name as status|0 as sign_up|0 as register|ifnull(v.visits, 0) as visits|a.activity_start_time|a.activity_end_time|a.activity_place|t1.code_name as activity_online_offline|t.code_name as activity_type|a.paid|g.fullname as name|a.id|a.sign_up_limit|a.sur_id|a.allow_onsite_checkin".split(
                '|'),
            table='''t_news as a
            left join (select ifnull(count(v1.id), 0) as visits, 
                visit_target from t_visit as v1, 
                t_news as a where v1.visit_target=concat('/page/event/', a.id) group by visit_target) as v on v.visit_target=concat('/page/event/', a.id)
            left join t_codes as m on a.status = m.code_id  
            left join t_codes as t on a.activity_type = t.code_id 
            left join (select code_id,code_name from t_codes where code_type='activity_online_offline') as t1 on a.activity_online_offline = t1.code_id 
            left join t_codes as n on a.status = n.code_id 
            left join t_person as g on a.person_id = g.person_id ''',
            sortcol='a.published ASC',
            req=self,
            searchcolumns='a.title,activity_place,t1.code_name,t.code_name,m.code_name,g.fullname',
            where="a.status !='deleted' and a.type='activity' %s" % where_cond)


@Route(r"/rest/mgr/discussion/table")
class _(MgrHandler):
    @assert_user
    @coroutine
    def get(self):
        profile = self.current_user_profile
        where_cond = ""
        if is_role_in(profile['roles'], ['eventmgr_ygzx']) and not is_role_in(profile['roles'], ['admin']):
            logging.info(profile['roles'])

            res = yield self.fetchone_db(
                r"""select ar.group_id org_id,group_concat(ar.person_id SEPARATOR '\',\'') person_ids from t_auth_role ar
                where ar.group_id in (select group_id from t_auth_role where person_id=%s)
                group by ar.group_id""", self.current_user)
            where_cond += "and a.person_id in ('%s') " % res['person_ids']

        res = yield response_datatable_result(
            columns="a.title|n.code_name as status|sum( case r.item_type when 'discussion' then 1 else 0 end ) as sign_up|ifnull(v.visits, 0) as visits|a.activity_start_time|a.activity_end_time|t1.code_name as activity_online_offline|a.subject|t.code_name as activity_type|g.fullname as name|a.id|a.sign_up_limit".split(
                '|'),
            table='''t_discussion as a
            left join (select ifnull(count(v1.id), 0) as visits, 
                visit_target from t_visit as v1, 
                t_discussion as a where v1.visit_target=concat('/page/discussion/', a.id) group by visit_target) as v on v.visit_target=concat('/page/discussion/', a.id)
            left join t_traffic as r on a.id = r.activity_id and r.item_type='discussion' 
            left join t_codes as t on a.activity_type = t.code_id 
            left join (select code_id,code_name from t_codes where code_type='activity_online_offline') as t1 on a.activity_online_offline = t1.code_id 
            left join t_codes as n on a.status = n.code_id 
            left join t_person as g on a.person_id = g.person_id ''',
            sortcol='a.published ASC',
            req=self,
            searchcolumns='a.title,activity_place,t1.code_name,t.code_name,n.code_name,g.fullname',
            where="a.status !='deleted' %s group by a.id " % where_cond)


@Route(r"/rest/mgr/activity/visit/table")
class _(MgrHandler):
    @assert_user
    @coroutine
    def get(self):
        activity_id = self.get_argument('activity_id')
        yield response_datatable_result(

            columns='''b.title as name|c.fullname|a.visit_count|a.first_visited|a.last_visited|concat('/page/discussion/', b.id) as link|concat('/page/wechat_info_', a.person_id) as auth_link'''.split(
                '|'),
            table='''
                                        t_visit as a
                                        left join t_news as b on a.visit_target = concat('/page/discussion/', b.id)
                                        left join t_person as c on c.person_id = a.person_id
                                       ''',
            sortcol='a.last_visited ASC',
            req=self,
            searchcolumns='',
            where="a.visit_target='/page/discussion/%s'" % activity_id)


@Route(r"/rest/mgr/discussion/visit/table")
class _(MgrHandler):
    @assert_user
    @coroutine
    def get(self):
        activity_id = self.get_argument('activity_id')
        yield response_datatable_result(

            columns='''b.title as name|c.fullname|a.visit_count|a.first_visited|a.last_visited|concat('/page/discussion/', b.id) as link|concat('/page/wechat_info_', a.person_id) as auth_link'''.split(
                '|'),
            table='''
                                        t_visit as a
                                        left join t_discussion as b on a.visit_target = concat('/page/discussion/', b.id)
                                        left join t_person as c on c.person_id = a.person_id
                                       ''',
            sortcol='a.last_visited ASC',
            req=self,
            searchcolumns='',
            where="a.visit_target='/page/discussion/%s'" % activity_id)


@Route(r"/rest/mgr/activity/sign_up_or_register/table")
class _(MgrHandler):
    @assert_user
    @coroutine
    def get(self):
        type = self.get_argument('type')
        activity_id = self.get_argument('activity_id')
        status_type = self.get_escaped_argument('status_type', '')
        condition = " t.item_type = '%s' and t.activity_id = '%s' and t.status!='deleted' " % (type, activity_id)
        if status_type:
            condition += " and t.status = '%s'" % (status_type)
        if type == "sign_up":
            condition += "and m.code_id = t.status and p.cellphone != '' group by person_id"
            yield response_datatable_result(
                columns="p.fullname,t.created,m.code_name,GROUP_CONCAT(tc.code_name) as member_type,t.is_volunteer,p.cellphone,GROUP_CONCAT(o.org_name) as org_name,p.position,p.email,p.wechatid,p.attachment,t.contribution,t.auth_id,t.activity_id,p.person_id,t.reason,t.status,t_news.sur_id,s.sur_value".split(
                    ','),
                table='''t_traffic as t
                                            left join t_person as p on p.person_id = t.person_id
                                            left join t_member as tm on tm.person_id = p.person_id
                                            left join t_codes as tc on tc.code_id=tm.member_type
                                            left join t_org_person as op on op.person_id = p.person_id 
                                            left join t_org as o on o.org_id = op.org_id
                                            left join t_news on t_news.id = t.activity_id
                                            left join t_codes as m on m.code_id = t.status
                                            left join (select ss.auth_id,group_concat(ans_value) as sur_value from
                                                        t_survey as s 
                                                        left join t_survey_answer as sa on s.sur_id = sa.sur_id
                                                        left join t_news on t_news.sur_id = s.sur_id
                                                        left join t_survey_submit as ss on ss.submit_id = sa.submit_id
                                                        where t_news.id = %s
                                                        group by ss.auth_id) as s on p.person_id = s.auth_id
                                            ''' % activity_id,
                sortcol='t.created ASC',
                req=self,
                searchcolumns='p.fullname,m.code_name,o.org_name,p.position,p.email,p.wechatid',
                where=condition)
        elif type == "register":
            condition += "group by person_id"
            yield response_datatable_result(
                columns='p.fullname,p.cellphone,GROUP_CONCAT(distinct tc.code_name) as member_type,GROUP_CONCAT(distinct o.org_name) as org_name,p.position,t.created,p.email,p.wechatid,p.attachment,p.person_id,t.reason,t.status,t.activity_id,p.person_id,t.reason,t.status,t_news.sur_id,s.sur_value'.split(
                    ','),
                table='''t_traffic as t 
                        left join t_person as p on p.person_id = t.person_id
                        left join t_member as tm on tm.person_id = p.person_id 
                        left join t_codes as tc on tc.code_id=tm.member_type 
                        left join t_org_person as op on op.person_id = p.person_id 
                        left join t_org as o on o.org_id = op.org_id
                        left join t_news on t_news.id = t.activity_id
                        left join t_codes as m on m.code_id = t.status
                        left join (select ss.auth_id,group_concat(ans_value) as sur_value from
                                t_survey as s 
                                left join t_survey_answer as sa on s.sur_id = sa.sur_id
                                left join t_news on t_news.sur_id = s.sur_id
                                left join t_survey_submit as ss on ss.submit_id = sa.submit_id
                                where t_news.id = %s
                                group by ss.auth_id) as s on p.person_id = s.auth_id
                        ''' % activity_id,
                sortcol='t.created ASC',
                req=self,
                searchcolumns='p.fullname,o.org_name,p.position,p.email,p.wechatid',
                where=condition)


@Route(r"/rest/mgr/discussion/sign_up/table")
class _(MgrHandler):
    @assert_user
    @coroutine
    def get(self):
        type = self.get_argument('type')
        activity_id = self.get_argument('activity_id')
        status_type = self.get_escaped_argument('status_type', '')
        condition = " t.item_type = '%s' and t.activity_id = '%s'" % (type, activity_id)
        if status_type:
            condition += " and t.status = '%s'" % (status_type)
            
        condition += "and m.code_id = t.status and p.cellphone != '' group by person_id"
        yield response_datatable_result(
            columns="p.fullname,t.created,m.code_name,GROUP_CONCAT(distinct tc.code_name) as member_type,t.is_volunteer,p.cellphone,GROUP_CONCAT(distinct o.org_name) as org_name,p.position,p.email,p.wechatid,p.attachment,t.contribution,t.auth_id,t.activity_id,p.person_id,t.reason,t.status".split(
                ','),
            table='''t_traffic as t
                                        left join t_person as p on p.person_id = t.person_id
                                        left join t_member as tm on tm.person_id = p.person_id
                                        left join t_codes as tc on tc.code_id=tm.member_type
                                        left join t_org_person as op on op.person_id = p.person_id 
                                        left join t_org as o on o.org_id = op.org_id
                                        left join t_discussion on t_discussion.id = t.activity_id
                                        left join t_codes as m on m.code_id = t.status
                                        ''',
            sortcol='t.created ASC',
            req=self,
            searchcolumns='p.fullname,m.code_name,o.org_name,p.position,p.email,p.wechatid',
            where=condition)
        

@Route(r"/rest/mgr/activity/sign_up_or_register/status")
class _(MgrHandler):
    @assert_user
    @coroutine
    def post(self):
        activity_id = self.get_escaped_argument("activity_id", "")
        person_id = self.get_escaped_argument("person_id", "")
        status = self.get_escaped_argument("status", "")
        reason = self.get_escaped_argument("reason", "")
        if person_id:
            ids = person_id.split(",")
        else:
            yield self.error("请选择需要修改状态的条目")
        if status not in ["sign_up_success_and_register"]:
            yield self.error("状态不符合")
            return

        for id in ids:
            res = yield self.fetchone_db(
                "select status from t_traffic where activity_id = %s and person_id = %s and item_type='sign_up'",
                activity_id, id)
            if res and res['status'] in ['sign_up_wait', 'sign_up_success']:
                res = yield self.update_db(
                    "update t_traffic set status=%s where activity_id=%s and person_id = %s and item_type='sign_up'",
                    'sign_up_success',
                    activity_id, id)
                args = {
                    'activity_id': activity_id,
                    'item_type': 'register',
                    'is_volunteer': 0,
                    'contribution': '',
                    'status': '',
                    'source': '',
                    'created': get_now_str(),
                    'person_id': id
                }
                res = yield self.fetchone_db(
                    "select status from t_traffic where activity_id = %s and person_id = %s and item_type='register'",
                    activity_id, id)
                if not res:
                    res = yield self.insert_db_by_obj('t_traffic', args)
        yield self.restful({
            "message": "状态修改成功"
        })


from wechatpy.enterprise.crypto import WeChatCrypto
from wechatpy.exceptions import InvalidSignatureException
from wechatpy.enterprise.exceptions import InvalidCorpIdException
from wechatpy.enterprise import parse_message, create_reply, WeChatClient



@Route(r"/rest/mgr/discussion/begin_discussion")
class _(MgrHandler):
    @assert_user
    @coroutine
    def post(self):
        activity_id = self.get_escaped_argument("activity_id", "")
        discussion = yield self.fetchone_db("select * from t_discussion where id=%s", activity_id)
        if discussion:
            client = WeChatClient(self.config['wechat_corpid'], self.config['wechat_corp_im_secret'])
            # 创建会话
            # 详情请参考
            # http://qydev.weixin.qq.com/wiki/index.php?title=企业会话接口说明
            # :param chat_id: 会话id。字符串类型，最长32个字符。只允许字符0-9及字母a-zA-Z,
            #                 如果值内容为64bit无符号整型：要求值范围在[1, 2^63)之间，
            #                 [2^63, 2^64)为系统分配会话id区间
            # :param name: 会话标题
            # :param owner: 管理员userid，必须是该会话userlist的成员之一
            # :param user_list: 会话成员列表，成员用userid来标识。会话成员必须在3人或以上，1000人以下
            # :return: 返回的 JSON 数据包
            # TsingData
            user_list = []
            admin_userid = self.config['discussion_admin_userid'].split(',')
            if admin_userid:
                owner = admin_userid[0]
            traffic =  yield self.query_db("select person_id from t_traffic where activity_id=%s and item_type='discussion' and status='sign_up_success'",activity_id)
            for item in traffic:
                person = yield self.fetchone_db("select * from t_person where person_id=%s", item['person_id'])
                if person and person['user_id']:
                    user_list.append(person['user_id'])
            user_list.append(admin_userid)


            body =  client.chat.create(activity_id,discussion['title'],owner,user_list)
            logging.info(body)
            body =  client.chat.send_text(owner,'group',activity_id,discussion['title'])
            logging.info(body)
            
        yield self.restful({
            "message": "开启成功"
        })

@Route(r"/rest/mgr/discussion/end_discussion")
class _(MgrHandler):
    @assert_user
    @coroutine
    def post(self):
        activity_id = self.get_escaped_argument("activity_id", "")
        discussion = yield self.fetchone_db("select * from t_discussion where id=%s",activity_id)
        if discussion:
            client = WeChatClient(self.config['wechat_corpid'], self.config['wechat_corp_im_secret'])
            body = client.chat.get(activity_id)
            logging.info(body)
            userlist = body.get('userlist')
            admin_userid = self.config['discussion_admin_userid'].split(',')
            if admin_userid:
                owner = admin_userid[0]
            #owner cannot quit -- reply system busy.
            # userlist.remove(owner)
            logging.info(userlist)
            for userid in userlist:
                client.chat.quit(activity_id,userid)

        yield self.restful({
            "message": "解散成功"
        })            


@Route(r"/rest/mgr/discussion/add_person")
class _(MgrHandler):
    @assert_user
    @coroutine
    def post(self):
        activity_id = self.get_escaped_argument("activity_id", "")
        person_ids = self.get_escaped_argument("person_ids", "")
        if person_ids:
            ids = person_ids.split(",")
            discussion = yield self.fetchone_db("select * from t_discussion where id=%s", activity_id)
            if discussion:
                client = WeChatClient(self.config['wechat_corpid'], self.config['wechat_corp_im_secret'])
                """
                修改会话
                详情请参考
                http://qydev.weixin.qq.com/wiki/index.php?title=企业会话接口说明
                :param chat_id: 会话 ID
                :param op_user: 操作人 userid
                :param name: 会话标题
                :param owner: 管理员userid，必须是该会话userlist的成员之一
                :param add_user_list: 会话新增成员列表，成员用userid来标识
                :param del_user_list: 会话退出成员列表，成员用userid来标识
                :return: 返回的 JSON 数据包
                """
                user_list = []
                for id in ids:
                    person = yield self.fetchone_db("select * from t_person where person_id=%s", id)
                    if person:
                        user_list.append(person['user_id'])
                admin_userid = self.config['discussion_admin_userid'].split(',')
                if admin_userid:
                    owner = admin_userid[0]
                body = yield client.chat.update(activity_id,owner,discussion['title'],owner,user_list,[])
                logging.info(body)
                body = yield client.chat.send_text(owner,'group',activity_id,discussion['title'])
                logging.info(body)

        else:
            yield self.error("请选择需要修改状态的条目")
            return
        
        yield self.restful({
            "message": "添加成功"
        })


@Route(r"/rest/mgr/discussion/sign_up/status")
class _(MgrHandler):
    @assert_user
    @coroutine
    def post(self):
        activity_id = self.get_escaped_argument("activity_id", "")
        person_id = self.get_escaped_argument("person_id", "")
        status = self.get_escaped_argument("status", "")
        reason = self.get_escaped_argument("reason", "")
        if person_id:
            ids = person_id.split(",")
        else:
            yield self.error("请选择需要修改状态的条目")
        if status not in ["sign_up_success", "sign_up_fail", "sign_up_full"]:
            yield self.error("状态不符合")
            return

        for id in ids:
            res = yield self.update_db(
                "update t_traffic set status=%s where activity_id=%s and person_id = %s and item_type='discussion'",
                'sign_up_success',
                activity_id, id)
        yield self.restful({
            "message": "状态修改成功"
        })


@Route(r"/rest/mgr/activity/sign/up/status")
class _(MgrHandler):
    @assert_user
    @coroutine
    def post(self):
        activity_id = self.get_escaped_argument("activity_id", "")
        person_id = self.get_escaped_argument("person_id", "")
        status = self.get_escaped_argument("status", "")
        reason = self.get_escaped_argument("reason", "")
        if person_id:
            ids = person_id.split(",")
        else:
            yield self.error("请选择需要修改状态的条目")
        if status not in ["sign_up_success", "sign_up_fail", "sign_up_full"]:
            yield self.error("状态不符合")
            return

        for id in ids:
            res = yield self.update_db(
                "update t_traffic set status=%s ,reason = %s where activity_id=%s and person_id = %s", status, reason,
                activity_id, id)
        yield self.restful({
            "message": "状态修改成功"
        })

        # else:
        #     yield self.error('网络错误，请检查重试')


@Route(r"/rest/mgr/activity/sign/up/sms")
class _(MgrHandler):
    # @asynchronous
    @coroutine
    def get_short_url(self, url):
        # 获取accesstoken与openid
        client = tornado.httpclient.AsyncHTTPClient()
        accesstoken = self.get_cache('weixin-access_token')
        if not accesstoken:
            request = tornado.httpclient.HTTPRequest(
                url='https://api.weixin.qq.com/cgi-bin/token?' +
                    urllib.urlencode({"appid": self.config['wechat_appid'], "secret": self.config['wechat_secret'],
                                      "grant_type": "client_credential"}),
                method="GET",
                validate_cert=False
            )
            resp = yield client.fetch(request)
            body = json.loads(resp.body)
            accesstoken = body['access_token']
            self.set_cache('weixin-access_token', accesstoken, 60)

        request = tornado.httpclient.HTTPRequest(
            url="https://api.weixin.qq.com/cgi-bin/shorturl?" +
                urllib.urlencode({"access_token": accesstoken}),
            body=dump_json({"action": "long2short", "long_url": url}),
            method="POST",
            validate_cert=False
        )
        resp = yield client.fetch(request)
        body = json.loads(resp.body)
        short_url = body['short_url']
        raise Return(short_url)

    @assert_user
    @coroutine
    def post(self):
        activity_id = self.get_escaped_argument("activity_id")
        person_id = self.get_escaped_argument("person_id")
        event = yield self.fetchone_db("select title,id,activity_start_time,activity_place from t_news where id = %s",
                                       activity_id)
        for i in person_id.split(','):
            u = yield self.fetchone_db("select * from t_person where person_id = %s", i)
            if u and u.cellphone and event:
                code = u.cellphone.strip()
                # code = '18911631389'
                uukey = 'event-access-' + i + '-' + str(event['id'])
                url = self.config['site_host_url'] + 'page/event/' + str(activity_id) + '?uuid=' + i + '&uukey=' + uukey
                url = yield self.get_short_url(url)
                self.set_cache(uukey, i, 86400 * 30)
                msg = self.config['event_signup_sms'] % {'url': str(url), 'name': event.title,
                                                         'time': event.activity_start_time,
                                                         'place': event.activity_place}
                logging.info(msg)
                yield send_message(code, msg, self.config)
        yield self.restful({
            "message": "报名短信已发送到手机"
        })
        return

@Route(r"/rest/mgr/discussion/sign/up/sms")
class _(MgrHandler):
    # @asynchronous
    @coroutine
    def get_short_url(self, url):
        # 获取accesstoken与openid
        client = tornado.httpclient.AsyncHTTPClient()
        accesstoken = self.get_cache('weixin-access_token')
        if not accesstoken:
            request = tornado.httpclient.HTTPRequest(
                url='https://api.weixin.qq.com/cgi-bin/token?' +
                    urllib.urlencode({"appid": self.config['wechat_appid'], "secret": self.config['wechat_secret'],
                                      "grant_type": "client_credential"}),
                method="GET",
                validate_cert=False
            )
            resp = yield client.fetch(request)
            body = json.loads(resp.body)
            accesstoken = body['access_token']
            self.set_cache('weixin-access_token', accesstoken, 60)

        request = tornado.httpclient.HTTPRequest(
            url="https://api.weixin.qq.com/cgi-bin/shorturl?" +
                urllib.urlencode({"access_token": accesstoken}),
            body=dump_json({"action": "long2short", "long_url": url}),
            method="POST",
            validate_cert=False
        )
        resp = yield client.fetch(request)
        body = json.loads(resp.body)
        short_url = body['short_url']
        raise Return(short_url)

    @assert_user
    @coroutine
    def post(self):
        activity_id = self.get_escaped_argument("activity_id")
        person_id = self.get_escaped_argument("person_id")
        event = yield self.fetchone_db("select title,id,activity_start_time from t_discussion where id = %s",
                                       activity_id)
        for i in person_id.split(','):
            u = yield self.fetchone_db("select * from t_person where person_id = %s", i)
            if u and u.cellphone and event:
                code = u.cellphone.strip()
                # # code = '18911631389'
                # uukey = 'event-access-' + i + '-' + str(event['id'])
                url = self.config['site_host_url'] + 'page/discussion/' + str(activity_id)
                url = yield self.get_short_url(url)
                # self.set_cache(uukey, i, 86400 * 30)
                # msg = self.config['event_signup_sms'] % {'url': str(url), 'name': event.title,
                #                                          'time': event.activity_start_time,
                #                                          'place': event.activity_place}
                msg = self.config['discussion_signup_sms'] % {'url': str(url), 'name': event.title,
                                                     'time': event.activity_start_time,
                                                     'group': event.title}
                yield send_message(code, msg, self.config)
        yield self.restful({
            "message": "报名短信已发送到手机"
        })
        return

@Route(r"/rest/mgr/get/mapcode")
class _(MgrHandler):
    @coroutine
    def get(self):
        t = self.get_argument('type')
        res = yield self.query_db("select * from t_codes where code_type = %s order by code_sort ASC", t)
        yield self.restful(res)


@Route(r"/rest/mgr/get/tagcode")
class _(MgrHandler):
    @coroutine
    def get(self):
        t = self.get_argument('type')
        res = yield self.query_db("select * from t_tag where tag_type = %s order by tag_sort DESC", t)
        yield self.restful(res)


@Route(r"/rest/mgr/set/tagcode")
class _(MgrHandler):
    @coroutine
    def get(self):
        args = self.get_args({
            'tag_type': '*',
            'tag_name': '*'
        })
        args = mixin_json(args, {
            'tag_id': generate_uuid(),
            'tag_sort': 1
        })
        res = yield self.insert_db_by_obj('t_tag', args)
        if res:
            yield self.restful({
                'message': '保存成功'
            })
        else:
            yield self.error('保存失败')


@Route(r"/rest/mgr/get/channel")
class _(MgrHandler):
    @coroutine
    def get(self):
        res = yield self.query_db(
            "select a.code_name as name,b.code_name as picture,a.code_id from t_codes as a left join t_codes as b on a.code_id = b.code_id where a.code_type='activity_source' and b.code_type='activity_picture'")
        yield self.restful(res)


@Route(r"/rest/mgr/get/channelinfo")
class _(MgrHandler):
    @assert_user
    @coroutine
    def get(self):
        res = yield response_datatable_result(columns='a.code_name as name,b.code_name as picture,a.code_id'.split(','),
                                              table='''
                                                t_codes as a left join t_codes as b on a.code_id = b.code_id
                                                 ''',
                                              sortcol='a.code_id ASC',
                                              req=self,
                                              searchcolumns="",
                                              where="a.code_type='activity_source' and b.code_type='activity_picture'")


@Route(r"/rest/mgr/channel/detail")
class _(MgrHandler):
    @assert_user
    @coroutine
    def get(self):
        id = self.get_argument("id", '')
        sql = "select a.code_name as name,b.code_name as picture,a.code_id from t_codes as a left join t_codes as b on a.code_id = b.code_id where a.code_id = %s and a.code_type='activity_source' and b.code_type='activity_picture'"
        result = yield self.fetchone_db(sql, id)
        if result:
            yield self.restful(result)
        else:
            yield self.error("")


@Route(r"/rest/mgr/channel/update/status")
class _(MgrHandler):
    @assert_user
    @coroutine
    def post(self):
        id = self.get_argument("id", '')
        sql = "delete from t_codes where code_id = %s"
        result = yield self.update_db(sql, id)
        if result:
            yield self.restful({
                "message": "状态修改成功"
            })
        else:
            yield self.error("")


@Route(r"/rest/mgr/channel/commit")
class _(MgrHandler):
    @assert_user
    @coroutine
    def post(self):
        auth = self.current_user_profile
        args = self.get_args('name,picture'.split(','))
        if not args:
            yield self.error('miss_param')
        id = self.get_argument("id", "")
        if id:
            _args = mixin_json({}, {
                'code_name': args['name']
            })
            res = yield self.update_db_by_obj('t_codes', _args, "code_id='%s' and code_type='activity_source'" % id)
            _args = mixin_json({}, {
                'code_name': args['picture']
            })
            res += yield self.update_db_by_obj('t_codes', _args, "code_id='%s' and code_type='activity_picture'" % id)
        else:
            id = generate_uuid()
            _args = mixin_json({}, {
                'code_id': id,
                'code_name': args['name'],
                'code_type': 'activity_source'
            })
            res = yield self.insert_db_by_obj('t_codes', _args)
            _args = mixin_json({}, {
                'code_id': id,
                'code_name': args['picture'],
                'code_type': 'activity_picture'
            })
            res += yield self.insert_db_by_obj('t_codes', _args)

        if res:
            yield self.restful({
                'message': '添加成功'
            })
        else:
            yield self.error('添加失败')


@Route(r"/rest/mgr/news/edit")
class _(MgrHandler):
    @assert_user
    @coroutine
    def post(self):
        auth = self.current_user_profile
        param = {
            'title': '*',
            'published': '*',
            'status': '*',
            'data_source': '',
            'data_type': '*',
            'id': '*',
            'subject': '',
            'pictures': '',
            'type': '*',
            'paid': '',
            'activity_type': '',
            'activity_online_offline': '',
            'activity_place': '',
            'activity_start_time': '',
            'activity_end_time': '',
            'activity_guider': '',
            'activity_sponsor': '',
            'activity_undertake': '',
            'activity_organizer': '',
            'activity_support': '',
            'activity_cooperate': '',
            'sign_up_check': '',
            'general_place': '',
            'sign_up_fields': '',
            'sur_id': '',
            'event_corp_auth': ''
        }
        args = self.get_args(param)
        args['content'] = self.get_argument('content', '')
        args['signup_content'] = self.get_argument('signup_content', '')
        if not args:
            yield self.error('miss_param')

        args = mixin_json(args, {
            'updated': get_now_str(),
            'mgr_id': auth['authorized']['auth_id'],
            'person_id': auth['authorized']['person_id']
        })
        res = yield self.update_db_by_obj("t_news", args, "id='%s'" % args['id'])
        if res:
            yield self.restful({
                'message': '修改成功'
            })
        else:
            yield self.error('修改失败')


@Route(r"/rest/mgr/news/edit/channel")
class _(MgrHandler):
    @assert_user
    @coroutine
    def post(self):
        auth = self.current_user_profile
        param = {
            'id': '*',
            'channel_fields': '*'
        }
        args = self.get_args(param)
        if not args:
            yield self.error('miss_param')
        args = mixin_json(args, {
            'updated': get_now_str(),
            'mgr_id': auth['authorized']['auth_id'],
            'person_id': auth['authorized']['person_id']
        })
        res = yield self.update_db_by_obj("t_news", args, "id='%s'" % args['id'])
        if res:
            yield self.restful({
                'message': '修改成功'
            })
        else:
            yield self.error('修改失败')


@Route(r"/rest/mgr/discussion/edit/channel")
class _(MgrHandler):
    @assert_user
    @coroutine
    def post(self):
        auth = self.current_user_profile
        param = {
            'id': '*',
            'channel_fields': '*'
        }
        args = self.get_args(param)
        if not args:
            yield self.error('miss_param')
        args = mixin_json(args, {
            'updated': get_now_str(),
            'mgr_id': self.current_user
        })
        res = yield self.update_db_by_obj("t_discussion", args, "id='%s'" % args['id'])
        if res:
            yield self.restful({
                'message': '修改成功'
            })
        else:
            yield self.error('修改失败')


@Route(r"/rest/mgr/news/commit")
class _(MgrHandler):
    @assert_user
    @coroutine
    def post(self):
        auth = self.current_user_profile
        param = {
            'title': '*',
            'published': '*',
            'status': '*',
            'data_source': '',
            'data_type': '*',
            'subject': '',
            'pictures': '',
            'type': '*',
            'paid': '',
            'activity_type': '',
            'activity_online_offline': '',
            'activity_place': '',
            'activity_start_time': '',
            'activity_end_time': '',
            'activity_guider': '',
            'activity_sponsor': '',
            'activity_undertake': '',
            'activity_organizer': '',
            'activity_support': '',
            'activity_cooperate': '',
            'sign_up_check': '',
            'general_place': '',
            'sign_up_fields': '',
            'sur_id': ''
        }
        args = self.get_args(param)
        args['content'] = self.get_argument('content', '')
        args['signup_content'] = self.get_argument('signup_content', '')
        if not args:
            yield self.error('miss_param')
        args = mixin_json(args, {
            'created': get_now_str(),
            'updated': get_now_str(),
            'mgr_id': auth['authorized']['auth_id'],
            'person_id': auth['authorized']['person_id']
        })
        res = yield self.insert_db_by_obj('t_news', args)
        if res:
            yield self.restful({
                'message': '添加成功'
            })
        else:
            yield self.error('添加失败')


@Route(r"/rest/mgr/news/update/status")
class _(MgrHandler):
    @assert_user
    @coroutine
    def post(self):
        id = self.get_argument("id", '')
        status = self.get_argument("status", '')
        all_status = ['published', 'deleted', 'draft']
        if status not in all_status:
            yield self.error("操作不允许")
        sql = "update t_news set status=%s where id = %s"
        result = yield self.update_db(sql, status, id)
        if result:
            yield self.restful({
                "message": "状态修改成功"
            })
        else:
            yield self.error("")


@Route(r"/rest/mgr/news/update/signup/status")
class _(MgrHandler):
    @assert_user
    @coroutine
    def post(self):
        id = self.get_argument("id", '')
        status = self.get_argument("status", '')
        all_status = ["0", "1"]
        if status not in all_status:
            yield self.error("操作不允许")
        sql = "update t_news set sign_up_limit=%s where id = %s"
        result = yield self.update_db(sql, status, id)
        if result:
            yield self.restful({
                "message": "状态修改成功"
            })
        else:
            yield self.error("")


@Route(r"/rest/mgr/discussion/update/signup/status")
class _(MgrHandler):
    @assert_user
    @coroutine
    def post(self):
        id = self.get_argument("id", '')
        status = self.get_argument("status", '')
        all_status = ["0", "1"]
        if status not in all_status:
            yield self.error("操作不允许")
        sql = "update t_discussion set sign_up_limit=%s where id = %s"
        result = yield self.update_db(sql, status, id)
        if result:
            yield self.restful({
                "message": "状态修改成功"
            })
        else:
            yield self.error("")


@Route(r"/rest/mgr/news/update/signupandregister/status")
class _(MgrHandler):
    @assert_user
    @coroutine
    def post(self):
        """
        修改活动是否开放签到，如果开放签到，那么用户可直接报名并签到（活动）
        :return:
        """
        id = self.get_argument("id", '')
        status = self.get_argument("status", '')
        all_status = ["0", "1"]
        if status not in all_status:
            yield self.error("操作不允许")
        sql = "update t_news set allow_onsite_checkin=%s where id = %s"
        result = yield self.update_db(sql, status, id)
        if result:
            yield self.restful({
                "message": "状态修改成功"
            })
        else:
            yield self.error("")


@Route(r"/rest/mgr/tag/add")
class _(MgrHandler):
    @assert_user
    @coroutine
    def post(self):
        auth = self.current_user_profile
        tag_type = self.get_argument('type')
        tag_name = self.get_argument('name')
        if not tag_type or not tag_name:
            yield self.error('miss_param')
            return

        res = yield self.fetchone_db("select * from t_tag where tag_type = %s and tag_name = %s", tag_type, tag_name)
        if res:
            yield self.error('错误：标签类型已经存在，请添加其他类型')
            return
        tag_id = self.get_argument('id', '')
        if not tag_id:
            args = {
                'tag_id': generate_uuid(),
                'tag_name': tag_name,
                'tag_type': tag_type,
                'tag_sort': 0
            }
            res = yield self.insert_db_by_obj("t_tag", args)
        else:
            args = {
                'tag_name': tag_name,
                'tag_type': tag_type,
                'tag_sort': 0
            }
            res = yield self.update_db_by_obj("t_tag", args, "tag_id='%s'" % tag_id)
        if res:
            args['message'] = '添加成功'
            yield self.restful(args)
        else:
            yield self.error('添加失败')


@Route(r"/rest/mgr/article/edit")
class _(MgrHandler):
    @assert_user
    @coroutine
    def post(self):
        auth = self.current_user_profile
        param = {
            'title': '*',
            'published': '*',
            'status': '*',
            'data_source': '',
            'data_type': '*',
            'id': '*',
            'subject': '',
            'pictures': '',
            'type': '*'
        }
        args = self.get_args(param)
        args['content'] = self.get_argument('content', '')
        if not args:
            yield self.error('miss_param')

        args = mixin_json(args, {
            'updated': get_now_str(),
            'mgr_id': auth['authorized']['auth_id']
        })
        res = yield self.update_db_by_obj("t_article", args, "id='%s'" % args['id'])
        if res:
            yield self.restful({
                'message': '修改成功'
            })
        else:
            yield self.error('修改失败')


@Route(r"/rest/mgr/article/commit")
class _(MgrHandler):
    @assert_user
    @coroutine
    def post(self):
        auth = self.current_user_profile
        param = {
            'title': '*',
            'published': '*',
            'status': '*',
            'data_source': '',
            'data_type': '*',
            'subject': '',
            'pictures': '',
            'type': '*'
        }
        args = self.get_args(param)
        args['content'] = self.get_argument('content', '')
        if not args:
            yield self.error('miss_param')
        args = mixin_json(args, {
            'created': get_now_str(),
            'updated': get_now_str(),
            'mgr_id': auth['authorized']['auth_id']
        })
        res = yield self.insert_db_by_obj('t_article', args)
        if res:
            yield self.restful({
                'message': '添加成功'
            })
        else:
            yield self.error('添加失败')


@Route(r"/rest/mgr/charge/detail/table")
class _(MgrHandler):
    @assert_user
    @coroutine
    def get(self):
        table_filters = [{
            "data": "created",
            "type": "text",
            "default": "",
            "condition": "a.created >= %s and a.created <= %s"
        }, {
            "data": "paid_start_time",
            "type": "text",
            "default": "",
            "condition": "a.paid_start_time >= %s and a.paid_start_time <= %s"
        }, {
            "data": "paid_end_time",
            "type": "text",
            "default": "",
            "condition": "a.paid_end_time >= %s and a.paid_end_time <= %s"
        }]
        res = []
        for f in table_filters:
            v1 = self.get_argument(f['data'], '')
            v2 = self.get_argument(f['data'] + '-2', '')
            if v1 or v2:
                if v1:
                    v1 = v1.replace("/", "-")
                if v2:
                    v2 = v2.replace("/", "-")
                res.append(f['condition'] % (
                    self.escape(v1 or '1999-01-01 00:00:00'), self.escape(v2 or '2999-01-01 00:00:00')))
        where = ""
        if res:
            where = ' and '.join(res) + " and "
        res = yield response_datatable_result(
            columns='p.fullname|code_name|left(a.paid_start_time,10) as paid_start_time|left(a.paid_end_time,10) as paid_end_time|a.paid_money|a.created|m.member_id'.split(
                '|'),
            table='''t_payment_record as a , t_member as m left join t_codes on code_id = m.member_type,t_person as p''',
            sortcol='a.created ASC',
            req=self,
            searchcolumns='p.fullname,code_name',
            where="%s a.form_id = m.form_id and m.person_id =p.person_id " % where)


@Route(r"/rest/mgr/dataset/table")
class _(MgrHandler):
    @assert_user
    @coroutine
    def get(self):
        res = yield response_datatable_result(
            columns='a.title|a.org_name|a.industry|t.tag_name as data_type|a.connect_person|a.connect_cellphone|left(a.created,10) as created|m.code_name as status|g.nick_name as name|a.id'.split(
                '|'),
            table='''t_dataset as a left join t_codes as m on a.status = m.code_id left join t_tag as t on a.data_type = t.tag_id ,
                                                        t_authorized_user as g ''',
            sortcol='a.created ASC',
            req=self,
            searchcolumns='',
            where="a.status !='deleted' and a.mgr_id = g.auth_id")


@Route(r"/rest/mgr/dataset/detail")
class _(MgrHandler):
    @assert_user
    @coroutine
    def get(self):
        id = self.get_argument("id", '')
        sql = "select * from t_dataset where id = %s"
        result = yield self.query_db(sql, id)
        if result:
            yield self.restful(result)
        else:
            yield self.error("")


@Route(r"/rest/mgr/dataset/update/status")
class _(MgrHandler):
    @assert_user
    @coroutine
    def post(self):
        id = self.get_argument("id", '')
        status = self.get_argument("status", '')
        all_status = ['published', 'deleted', 'draft']
        if status not in all_status:
            yield self.error("操作不允许")
        sql = "update t_dataset set status=%s where id = %s"
        result = yield self.update_db(sql, status, id)
        if result:
            yield self.restful({
                "message": "状态修改成功"
            })
        else:
            yield self.error("")


@Route(r"/rest/mgr/dataset/edit")
class _(MgrHandler):
    @assert_user
    @coroutine
    def post(self):
        auth = self.current_user_profile
        param = {
            'id': '*',
            'status': '*',
            'title': '*',
            'org_name': '*',
            'industry': '*',
            'org_type': '*',
            'data_type': '*',
            'connect_person': '*',
            'connect_cellphone': '*',
            'org_describle': '*',
            'data_describle': '*',
            'content': '*',
            'pictures': '',
            'attachments': ''
        }
        args = self.get_args(param)
        args['content'] = self.get_argument('content', '')
        if not args:
            yield self.error('miss_param')

        args = mixin_json(args, {
            'updated': get_now_str(),
            'mgr_id': auth['authorized']['auth_id']
        })
        res = yield self.update_db_by_obj("t_dataset", args, "id='%s'" % args['id'])
        if res:
            yield self.restful({
                'message': '修改成功'
            })
        else:
            yield self.error('修改失败')


@Route(r"/rest/mgr/dataset/commit")
class _(MgrHandler):
    @assert_user
    @coroutine
    def post(self):
        auth = self.current_user_profile
        param = {
            'title': '*',
            'org_name': '*',
            'status': '*',
            'industry': '*',
            'org_type': '*',
            'data_type': '*',
            'connect_person': '*',
            'connect_cellphone': '*',
            'org_describle': '*',
            'data_describle': '*',
            'content': '*',
            'pictures': '',
            'attachments': ''
        }
        args = self.get_args(param)
        args['content'] = self.get_argument('content', '')
        if not args:
            yield self.error('miss_param')
        args = mixin_json(args, {
            'created': get_now_str(),
            'updated': get_now_str(),
            'mgr_id': auth['authorized']['auth_id']
        })
        res = yield self.insert_db_by_obj('t_dataset', args)
        if res:
            yield self.restful({
                'message': '添加成功'
            })
        else:
            yield self.error('添加失败')


@Route(r"/rest/mgr/article/update/status")
class _(MgrHandler):
    @assert_user
    @coroutine
    def post(self):
        id = self.get_argument("id", '')
        status = self.get_argument("status", '')
        all_status = ['published', 'deleted', 'draft']
        if status not in all_status:
            yield self.error("操作不允许")
        sql = "update t_article set status=%s where id = %s"
        result = yield self.update_db(sql, status, id)
        if result:
            yield self.restful({
                "message": "状态修改成功"
            })
        else:
            yield self.error("")


@Route(r"/rest/mgr/news/detail")
class _(MgrHandler):
    @assert_user
    @coroutine
    def get(self):
        id = self.get_argument("id", '')
        sql = """
            select title,subject,left(published,10) as published, content ,
                    data_source, data_type, pictures ,activity_start_time,
                    activity_end_time,activity_guider,activity_undertake,activity_sponsor,
                    activity_place,activity_type,activity_online_offline,
                    paid,sign_up_check,general_place,signup_content,sign_up_fields,
                    a.sur_id,b.sur_title,activity_organizer,activity_support,activity_cooperate,channel_fields,event_corp_auth
                    from t_news as a LEFT JOIN t_survey as b on b.sur_id = a.sur_id where id = %s
            """
        result = yield self.query_db(sql, id)
        if result:
            yield self.restful(result)
        else:
            yield self.error("")


@Route(r"/rest/mgr/discussion/detail")
class _(MgrHandler):
    @assert_user
    @coroutine
    def get(self):
        id = self.get_argument("id", '')
        sql = """
            select title,subject,left(published,10) as published, content ,
                    data_type, pictures ,activity_start_time,
                    activity_end_time,activity_type,activity_online_offline,
                    sign_up_check,signup_content,sign_up_fields,
                    channel_fields
                    from t_discussion as a where id = %s
            """
        result = yield self.query_db(sql, id)
        if result:
            yield self.restful(result)
        else:
            yield self.error("")


@Route(r"/rest/mgr/article/detail")
class _(MgrHandler):
    @assert_user
    @coroutine
    def get(self):
        id = self.get_argument("id", '')
        sql = "select title,subject,left(published,10) as published, content , data_source, data_type, pictures  from t_article where id = %s"
        result = yield self.query_db(sql, id)
        if result:
            yield self.restful(result)
        else:
            yield self.error("")


@Route(r"/rest/mgr/requirement/table")
class _(MgrHandler):
    @assert_user
    @coroutine
    def get(self):
        res = yield response_datatable_result(
            columns='a.title|m.code_name as status|left(a.published,10) as published|a.updated|a.contact_name|a.contact_cellphone|a.contact_wechatid|g.nick_name as name|a.id'.split(
                '|'),
            table='''t_requirement as a left join t_codes as m on a.status = m.code_id
                      left join t_authorized_user as g on g.auth_id=a.auth_id''',
            sortcol='a.published ASC',
            req=self,
            searchcolumns='a.title,published,a.data_source,m.code_name',
            where="a.status !='deleted' ")


@Route(r"/rest/mgr/requirement/detail")
class _(MgrHandler):
    @assert_user
    @coroutine
    def get(self):
        id = self.get_argument("id", '')
        sql = "select *  from t_requirement where id = %s"
        result = yield self.query_db(sql, id)
        if result:
            yield self.restful(result)
        else:
            yield self.error("")


@Route(r"/rest/mgr/requirement/update/status")
class _(MgrHandler):
    @assert_user
    @coroutine
    def post(self):
        id = self.get_argument("id", '')
        status = self.get_argument("status", '')
        all_status = ['published', 'deleted', 'draft', 'submitted', 'back']
        if status not in all_status:
            yield self.error("操作不允许")
        if status == 'published':
            sql = "update t_requirement set status=%s , published=%s where id = %s"
            result = yield self.update_db(sql, status, get_now_str(), id)
        else:
            sql = "update t_requirement set status=%s where id = %s"
            result = yield self.update_db(sql, status, id)
        if result:
            yield self.restful({
                "message": "状态修改成功"
            })
        else:
            yield self.error("")


@Route(r"/rest/mgr/requirement/commit")
class _(MgrHandler):
    @assert_user
    @coroutine
    def post(self):
        auth = self.current_user_profile
        args = self.get_args(
            'status,title,contact_name,contact_cellphone,contact_wechatid,repay_content,intro_content,attachments'.split(
                ','))
        if not args:
            yield self.error('miss_param')
        if not is_valid_phone(args['contact_cellphone']):
            yield self.error("请输入正确的电话号码")
            return
        args['content'] = self.get_argument("content")
        if args['status'] == 'published':
            args['published'] = get_now_str()
        id = self.get_argument("id", "")
        auth_info = yield self.fetchone_db("select auth_id from t_authorized_user where cellphone=%s",
                                           args['contact_cellphone'])
        auth_id = ""
        if auth_info:
            auth_id = auth_info['auth_id']
        if id:
            args = mixin_json(args, {
                'updated': get_now_str(),
                'mgr_id': auth['authorized']['auth_id'],
                'auth_id': auth_id
            })
            res = yield self.update_db_by_obj('t_requirement', args, "id=%s" % id)
        else:
            args = mixin_json(args, {
                'created': get_now_str(),
                'updated': get_now_str(),
                'mgr_id': auth['authorized']['auth_id'],
                'auth_id': auth_id
            })
            res = yield self.insert_db_by_obj('t_requirement', args)
        if res:
            yield self.restful({
                'message': '添加成功'
            })
        else:
            yield self.error('添加失败')


@Route(r"/rest/mgr/survey/table")
class _(MgrHandler):
    @assert_user
    @coroutine
    def get(self):
        profile = self.current_user_profile
        if is_role_in(profile['roles'], ['eventmgr_ygzx']) and not is_role_in(profile['roles'], ['admin']):
            logging.info(profile['roles'])

            res = yield self.query_db(
                "select person_id from t_auth_role where role_id='eventmgr_ygzx' and role_id!='admin'")
            id_list = []
            for item in res:
                id_list.append(item['person_id'])
            logging.info("','".join(id_list))
            res = yield response_datatable_result(
                columns='a.sur_title as title|m.code_name as status|ifnull(s.submit_count, 0) as submit_count|a.sur_created as created|a.sur_updated as updated|ifnull(q.quiz_count, 0) as quiz_count|a.sur_id as id'.split(
                    '|'),
                table='''t_survey as a left join t_codes as m on a.sur_status = m.code_id and m.code_type = 'status'
                                  left join t_authorized_user as g on g.auth_id=a.auth_id
                                  left join (select count(submit_id) as submit_count, sur_id from t_survey_submit group by sur_id) as s on s.sur_id = a.sur_id
                                  left join (select count(quiz_id) as quiz_count, sur_id from t_survey_quiz group by sur_id) as q on q.sur_id = a.sur_id
                                  ''',
                sortcol='a.sur_updated DESC',
                req=self,
                searchcolumns='a.sur_title,a.sur_created,m.code_name',
                where="a.sur_status !='deleted' and a.auth_id in ('%s')" % "','".join(id_list))
        else:
            res = yield response_datatable_result(
                columns='a.sur_title as title|m.code_name as status|ifnull(s.submit_count, 0) as submit_count|a.sur_created as created|a.sur_updated as updated|ifnull(q.quiz_count, 0) as quiz_count|a.sur_id as id'.split(
                    '|'),
                table='''t_survey as a left join t_codes as m on a.sur_status = m.code_id and m.code_type = 'status'
                          left join t_authorized_user as g on g.auth_id=a.auth_id
                          left join (select count(submit_id) as submit_count, sur_id from t_survey_submit group by sur_id) as s on s.sur_id = a.sur_id
                          left join (select count(quiz_id) as quiz_count, sur_id from t_survey_quiz group by sur_id) as q on q.sur_id = a.sur_id
                          ''',
                sortcol='a.sur_updated DESC',
                req=self,
                searchcolumns='a.sur_title,a.sur_created,m.code_name',
                where="a.sur_status !='deleted' ")


@Route(r"/rest/mgr/survey/commit")
class _(MgrHandler):
    @assert_user
    @coroutine
    def post(self):
        auth = self.current_user_profile
        args = self.get_args('sur_status,sur_title,sur_image'.split(','))
        if not args:
            yield self.error('miss_param')
        args['sur_content'] = self.get_argument("sur_content", '')
        id = self.get_argument("id", "")
        if id:
            args = mixin_json(args, {
                'sur_updated': get_now_str(),
                'auth_id': auth['authorized']['auth_id']
            })
            res = yield self.update_db_by_obj('t_survey', args, "sur_id='%s'" % id)
        else:
            id = generate_uuid()
            args = mixin_json(args, {
                'sur_id': id,
                'sur_created': get_now_str(),
                'sur_updated': get_now_str(),
                'auth_id': auth['authorized']['auth_id']
            })
            res = yield self.insert_db_by_obj('t_survey', args)
        quizs = json.loads(self.get_argument("quizs", '[]'))
        yield self.execute_db("delete from t_survey_quiz where sur_id = %s", id)
        for q in quizs:
            yield self.execute_db('''
                INSERT INTO t_survey_quiz (quiz_id, quiz_title, quiz_type, quiz_created, quiz_updated, quiz_sort, quiz_is_required, sur_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                    quiz_title=%s, quiz_type=%s, quiz_created=%s, quiz_updated=%s, quiz_sort=%s, quiz_is_required=%s
                ''',
                                  q['id'], q['title'], q['type'], get_now_str(), get_now_str(), q['sort'],
                                  q['required'], id,
                                  q['title'], q['type'], get_now_str(), get_now_str(), q['sort'], q['required'])
            yield self.execute_db("delete from t_survey_quizopt where quiz_id = %s", q['id'])
            if q['opts']:
                for o in q['opts']:
                    yield self.execute_db('''
                        INSERT INTO t_survey_quizopt (qopt_id, qopt_title, qopt_created, qopt_updated, qopt_sort, quiz_id)
                            VALUES (%s, %s, %s, %s, %s, %s)
                            ON DUPLICATE KEY UPDATE
                            qopt_title=%s, qopt_updated=%s, qopt_sort=%s
                        ''',
                                          o['id'], o['title'], get_now_str(), get_now_str(), o['sort'], q['id'],
                                          o['title'], get_now_str(), o['sort'])

        if res:
            yield self.restful({
                'message': '添加成功'
            })
        else:
            yield self.error('添加失败')


@Route(r"/rest/mgr/survey/detail")
class _(MgrHandler):
    @assert_user
    @coroutine
    def get(self):
        id = self.get_argument("id", '')
        sql = "select * from t_survey where sur_id = %s"
        result = yield self.fetchone_db(sql, id)
        quizs = yield self.query_db(
            "select quiz_id as id, quiz_title as title, quiz_type as type, quiz_sort as sort, quiz_is_required as required from t_survey_quiz where sur_id = %s order by quiz_sort ASC",
            id)
        for q in quizs:
            q['opts'] = yield self.query_db(
                "select qopt_id as id, qopt_title as title, qopt_sort as sort from t_survey_quizopt where quiz_id = %s order by qopt_sort ASC",
                q['id'])
        result['quizs'] = quizs
        if result:
            yield self.restful(result)
        else:
            yield self.error("")


@Route(r"/rest/mgr/survey/(.*)/user/(.*)")
class _(MgrHandler):
    @assert_user
    @coroutine
    def get(self, sur_id, user_id):
        survey = yield get_survey(self, sur_id, user_id)
        yield self.restful(survey)


@Route(r"/rest/mgr/survey/update/status")
class _(MgrHandler):
    @assert_user
    @coroutine
    def post(self):
        id = self.get_argument("id", '')
        status = self.get_argument("status", '')
        all_status = ['published', 'deleted', 'draft']
        if status not in all_status:
            yield self.error("操作不允许")
        sql = "update t_survey set sur_status=%s where sur_id = %s"
        result = yield self.update_db(sql, status, id)
        if result:
            yield self.restful({
                "message": "状态修改成功"
            })
        else:
            yield self.error("")


@Route(r"/rest/mgr/survey/choices")
class _(MgrHandler):
    @assert_user
    @coroutine
    def get(self):
        keyword = self.get_argument("keyword", '')
        if keyword:
            sql = "select sur_title as title, sur_id as id from t_survey where sur_status <> 'deleted' and inStr(sur_title, %s) > 0 order by sur_created DESC limit 0, 5"
            result = yield self.query_db(sql, keyword)
        else:
            sql = "select sur_title as title, sur_id as id from t_survey where sur_status <> 'deleted' order by sur_created DESC limit 0, 5"
            result = yield self.query_db(sql)
        yield self.restful(result)


@Route(r"/rest/mgr/logout")
class _(MgrHandler):
    @coroutine
    def post(self):
        res, msg = yield auth.logout_mgr(self)
        redirect = self.get_argument('redirect', '')
        if redirect:
            self.redirect("/mgr/login?redirect=logout")
        else:
            yield self.restful({
                'message': msg
            })

    @coroutine
    def get(self):
        yield self.post()


@Route(r"/rest/mgr/stats/construct")
class _(MgrHandler):
    @coroutine
    def get(self):
        k = "mgr-construct-traffic-status-global"
        if self.get_cache(k):
            yield self.restful({
                "construct_stats": False
            })
            return

        self.set_cache(k, 86400, 86400)
        res = yield self.execute_db("delete from ac_traffic_stats")
        res = yield self.insert_db('''
            insert into ac_traffic_stats
            select item_id, item_type,
            count(item_id) as traffic_count,
            max(created) as last_visited
             from ac_traffic group by item_id, item_type
            ''')
        yield self.restful({
            "construct_stats": res
        })


@Route(r"/fileupload/mgr/image")
class ImageFileUploadHandler(MgrHandler):
    @coroutine
    def head(self):
        yield self.response_as_json({})

    @coroutine
    def get(self):
        yield self.response_as_json({})

    @coroutine
    def post(self):
        if not self.request.files or (not 'files[]' in self.request.files and not 'file' in self.request.files):
            yield self.response_error('order_no_file')
            return

        f = self.request.files['files[]'][0] if 'files[]' in self.request.files else self.request.files['file'][0]
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

        f_url = '/assets/ticket/image/' + f_uun  # .replace('.', '/' + filename.split('.')[0] + '.')

        # 记住是该用户上传的文件
        # self.set_cache(str(user_id) + f_url, f_url, 3600*24)

        yield self.response_as_json({
            'files':
                [
                    {
                        'url': f_url,
                        'thumbnail_url': f_url,
                        'name': filename,
                        'type': 'image/' + f_type,
                        'size': len(f_data),
                        'delete_url': "/delete /file/",
                        'delete_type': "DELETE"
                    }
                ]
        })
