#!/usr/bin/python
# -*- coding: utf-8 -*-

import uuid, time, random, datetime
from util.server_side import DataTable
from util import read_file, write_file
from _base import genenate_file_key
from tornado.gen import coroutine, Return
import time, StringIO
from PIL import Image
import map_config
from page_config import *
import copy

def get_page_by_entry(entry):
    return copy.deepcopy(next((x for x in PAGES if x['id'] == entry), PAGES[0]))

def get_common_page_by_entry(entry):
    return copy.deepcopy(next((x for x in COMMON_PAGES if x['id'] == entry), PAGES[0]))

def get_body_page_by_entry(entry):
    return copy.deepcopy(next((x for x in MGR_PAGES + BODY_PAGES + COMMON_PAGES + LOGIN_PAGES if x['id'] == entry), MGR_PAGES[0]))

def get_mgr_page_by_entry(entry, mgr = None):
    page = copy.deepcopy(next((x for x in MGR_PAGES + LOGIN_PAGES if x['id'] == entry), MGR_PAGES[0]))
    return page 

def get_all_mgr_pages():
    return copy.deepcopy(MGR_PAGES)



def get_console_pages_ids():
    res = []
    for i in CONSOLE_PAGES:
        res.append(i['id'])
        if 'items' in i:
            for j in i['items']:
                res.append(j['id'])
    return res


def generate_uuid():
    return str(uuid.uuid1())

def generate_uunum():
    return str(int((time.time() - 3600*24*365*44)*100)) + str(random.randint(1000, 9999))

def mixin_json(obj1, obj2):
    for k in obj2:
        obj1[k] = obj2[k]
    return obj1

def get_now_str():
    return datetime.datetime.now().strftime("%y-%m-%d %H:%M:%S")



@coroutine
def get_datatable_result(*args, **aws):
    dt = DataTable(*args, **aws)
    res = {}
    yield dt.query(res)
    raise Return(res['output'])

@coroutine
def response_datatable_result(*args, **aws):
    handler = aws['req']
    aws['isexport'] = handler.get_argument('export', '')
    aws['isprint'] = handler.get_argument('print', '')
    dt = DataTable(*args, **aws)
    res = {}
    yield dt.query(res)
    
    if aws['isexport']:
        cols = handler.get_argument('cols', '').split(',')
        body = ''
        try:
            body = handler.get_argument('headers', '').decode('utf-8').encode('gbk').replace(',', '\t') + '\n'
        except:
            print 'header response error in table'
        for d in res['output']['data']:
            line = ''
            for c in cols:
                if c in d:
                    l = d[c].strip().replace('\t', '').replace('\n', '').replace('\r', '')
                    try:
                        l = l.decode('utf-8').encode('gbk')
                    except:
                        print 'error for coding'
                    line += l + '\t'
            body += line + '\n'
        fname = handler.get_argument('filename', 'table.xls')
        handler.set_header('Set-Cookie','fileDownload=true; path=/')
        handler.set_header("Content-Type", 'text/csv')
        handler.set_header("Content-Disposition", "attachment;filename=%s" % fname)
        handler.write(body)
        handler.finish()
        yield handler.close_db_conn()
    elif aws['isprint']:
        cols = handler.get_argument('cols', '').split(',')
        body = []
        try:
            body.append(handler.get_argument('headers', '').split(','))
        except:
            print 'header response error in table'
        for d in res['output']['data']:
            line = []
            for c in cols:
                if c in d:
                    l = d[c].strip().replace('\t', '').replace('\n', '').replace('\r', '')
                    line.append(l)
            body.append(line)
        ctx = {
            'items': body,
            'title': handler.get_argument('filename', '打印预览')
        }
        page = get_body_page_by_entry("mgr_print")
        handler.render(page['layout'], 
                    entry = page['id'],
                    page = page,
                    page_config = map_config,
                    context = ctx)
    else:
        yield handler.restful(res['output'])
        



def get_adjust_image(filepath, f_type = 'jpg', max_width = 1280):
    data = read_file(filepath)
    data = get_adjust_image_data(data, max_width)
    f_uun = genenate_file_key(data) + '.' + f_type

    write_file(f_uun, data)

    return f_uun

def get_thumb_image(filepath, f_type = 'jpg'):
    return get_adjust_image(filepath, f_type, max_width = 680)

def get_adjust_image_data(data, max_width = 1280):
    im = Image.open(StringIO.StringIO(data))
    print "uploaded im =", im.mode, im.size

    xsize, ysize = im.size

    if xsize > max_width:
        im = im.resize((max_width, int(ysize * max_width / xsize)), Image.ANTIALIAS)
        print 'resize', im.size

    strio = StringIO.StringIO()
    im.save(strio, 'JPEG', quality=80)
    strio.seek(0)
    f_data = strio.read()
    return f_data


@coroutine
def get_survey(self, id, user = '', with_submits = False):
    survey = yield self.fetchone_db("""
        select sur_title as title, sur_id as id, sur_content as content, sur_created as created,
               sur_updated as updated, sur_status as status, sur_image as image, auth_id 
               from t_survey where sur_id = %s
        """, id)
    quizs  = yield self.query_db("""
        select quiz_id as id, quiz_title as title, quiz_type as type, quiz_default as default_value, quiz_is_required as required,
        quiz_created as created, quiz_updated as updated, quiz_sort as sort, sur_id 
        from t_survey_quiz where sur_id = %s order by quiz_sort ASC
        """
        , id)

    for q in quizs:
        if q['type'] in ['select', 'checkbox']:
            q['opts'] = yield self.query_db("""
                select qopt_id as id, qopt_title as title, qopt_created as created, qopt_updated as updated, qopt_sort as sort, 
                quiz_id
                from t_survey_quizopt where quiz_id = %s order by qopt_sort ASC
                """, q['id'])
        else:
            q['opts'] = []

    survey['quizs'] = quizs

    if with_submits:
        submits_res = yield self.query_db('''
            select a.submit_id as id, a.sur_id, a.submit_created as created,
                    u.nick_name, u.head_img_url, u.cellphone,
                    b.ans_id, b.ans_value, b.ans_created, o.qopt_title as ans_label,
                    b.auth_id, b.quiz_id, q.quiz_sort
            from t_survey_submit as a
                left join t_authorized_user as u on u.auth_id = a.auth_id, 
                 t_survey_answer as b left join t_survey_quizopt as o on o.quiz_id = b.quiz_id and o.qopt_id = b.ans_value,
                 t_survey_quiz as q 
            where a.sur_id = %s and b.submit_id = a.submit_id and q.quiz_id = b.quiz_id
            order by a.submit_id ASC, q.quiz_sort ASC, a.submit_created DESC
            ''', id)
        submits = []
        for s in submits_res:
            if submits and submits[-1]['id'] == s['id']:
                if submits[-1]['quizs'][-1]['id'] == s['quiz_id']:
                    submits[-1]['quizs'][-1]['answers'].append({
                        'id': s['ans_id'],
                        'value': s['ans_value'],
                        'created': s['ans_created'],
                        'label': s['ans_label']
                    })
                else:
                    submits[-1]['quizs'].append({
                        'id': s['quiz_id'],
                        'sort': s['quiz_sort'],
                        'answers': [{
                            'id': s['ans_id'],
                            'value': s['ans_value'],
                            'created': s['ans_created'],
                            'label': s['ans_label']
                        }]
                    })
            else:
                submits.append({
                    'id': s['id'],
                    'sur_id': s['sur_id'],
                    'created': s['created'],
                    'nick_name': s['nick_name'],
                    'head_img_url': s['head_img_url'],
                    'cellphone': s['cellphone'],
                    'auth_id': s['auth_id'],
                    'quizs': [{
                        'id': s['quiz_id'],
                        'sort': s['quiz_sort'],
                        'answers': [{
                            'id': s['ans_id'],
                            'value': s['ans_value'],
                            'created': s['ans_created'],
                            'label': s['ans_label']
                        }]
                    }]
                })
        survey['submits'] = submits

    if user:
        submit = yield self.fetchone_db("""
            select submit_id as id, auth_id, sur_id, submit_created as created
            from t_survey_submit 
            where sur_id = %s and 
                ((auth_id = %s and auth_id <> '') or (submit_id = %s))
            """, id, user, user)
        if submit:
            answers = yield self.query_db("""
                select a.ans_id as id, a.ans_value as value, a.ans_created as created, 
                       a.auth_id, a.quiz_id, a.submit_id, ifnull(o.qopt_title, '') as label
                    from t_survey_answer as a
                        left join t_survey_quizopt as o on o.quiz_id = a.quiz_id and o.qopt_id = a.ans_value
                    where a.submit_id = %s
                """, submit['id'])
            survey['submit'] = submit
            survey['answers'] = answers
            for a in answers:
                for q in quizs:
                    if a['quiz_id'] == q['id']:
                        if 'answers' not in q:
                            q['answers'] = [a]
                        else:
                            q['answers'].append(a)
    
    raise Return(survey)

@coroutine
def post_survey(self, id, user = ''):
    survey = yield self.fetchone_db("""
        select sur_title as title, sur_id as id, sur_content as content, sur_created as created,
               sur_updated as updated, sur_status as status, sur_image as image, person_id 
               from t_survey where sur_id = %s
        """, id)
    if not survey:
        raise Return({'error': "调查表单不存在，请检查重试！"})
        return

    quizs  = yield self.query_db("""
        select quiz_id as id, quiz_title as title, quiz_type as type, quiz_default as default_value, quiz_is_required as required,
        quiz_created as created, quiz_updated as updated, quiz_sort as sort, sur_id 
        from t_survey_quiz where sur_id = %s order by quiz_sort ASC
        """
        , id)

    args = {}
    submit_id = generate_uuid()
    for q in quizs:
        a = self.get_arguments(q['id'])
        if q['required'] and a == []:
            yield self.execute_db("delete from t_survey_answer where submit_id = %s", submit_id)
            raise Return({'error': "请填写必填项：%s" % q['title']})
            return
        args[q['id']] = a
        for i in a:
            i = i.split('!!!!')
            for j in i:
                yield self.insert_db_by_obj('t_survey_answer', {
                    'ans_id': generate_uuid(),
                    'ans_value': j,
                    'ans_created': get_now_str(),
                    'person_id': user or '',
                    'quiz_id': q['id'],
                    "submit_id": submit_id,
                    'sur_id': id
                })

    submit_args = {
        'submit_id': submit_id,
        'person_id': user or '',
        'sur_id': id,
        'submit_created': get_now_str()
    }
    yield self.insert_db_by_obj('t_survey_submit', submit_args)

    self.set_secure_cookie(id, submit_id, expires_days = 1300)

    raise Return(True)

