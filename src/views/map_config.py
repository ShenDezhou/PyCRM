#!/usr/bin/python
# -*- coding: utf-8 -*-

import json, os
from lib import asynctorndb
import sys
sys.path.insert(0, "..")


MIME_TYPE = [{"id": l.strip().split(' ')[0].replace('.', ''), "name": l.strip().split(' ')[-1], "type": l.strip().split(' ')[-1]} for l in open(os.path.join(os.path.dirname(__file__), "constants/mime_types.txt"), "rb").read().split('\n')]
MIME_TYPE_DICT = {}
for l in open(os.path.join(os.path.dirname(__file__), "constants/mime_types.txt"), "rb").read().split('\n'):
    k = l.strip().split(' ')[0].replace('.', '')
    if k not in MIME_TYPE_DICT:
        MIME_TYPE_DICT[k] = l.strip().split(' ')[-1]

ASSET_INFO =  json.loads(open(os.path.join(os.path.dirname(__file__), "constants/asset_info.json"), "rb").read())
ASSET_NAME =  json.loads(open(os.path.join(os.path.dirname(__file__), "constants/asset_name.json"), "rb").read())
ASSET_UNIT = json.loads(open(os.path.join(os.path.dirname(__file__), "constants/asset_unit.json"), "rb").read())
MGR_DOCS = json.loads(open(os.path.join(os.path.dirname(__file__), "constants/mgr_docs.json"), "rb").read())


SIGN_UP_STATUS = []
ASSET_TYPE = []
LAND_TYPE = []
MACHINE_PROPERTY = []
PLANT_PROPERTIES = []
PROPERTY_ATTRIBUTE = []
STOCK_PROPERTY = []
HOUSE_PROPERTY = []
BANK_CATEGORY = []
DISTRICT_CATEGORY = []
CBRC_TYPE = []

SIGN_UP_STATUS_DICT = {}
ASSET_TYPE_DICT = {}
LAND_TYPE_DICT = {}
MACHINE_PROPERTY_DICT = {}
PLANT_PROPERTIES_DICT = {}
PROPERTY_ATTRIBUTE_DICT = {}
STOCK_PROPERTY_DICT = {}
HOUSE_PROPERTY_DICT = {}
BANK_CATEGORY_DICT = {}
DISTRICT_CATEGORY_DICT = {}
CBRC_TYPE_DICT = []

def get_formated_number_unit(value):
    if value == 'None':
        return ''
    if not value and value is not 0:
        return ''
    value = float(value)
    if value >= 100000000:
        return '亿'
    elif value >= 10000:
        return '万'
    else:
        return ''

def get_formated_number_value(value, no_scale = False):
    if value == 'None':
        return '-.-'
    if not value and value is not 0:
        return ''
    value = float(value)
    if no_scale:
        return "{:,.2f}".format(value)
    if value >= 100000000:
        value = value / 100000000
    elif value >= 10000:
        value = value / 10000
    return "{:,.2f}".format(value)

def get_formated_number(value, unit = '', place = 2):
    if not value and value is not 0:
        return ''
    value = float(value)
    fvalue = get_formated_number_value(value)
    unit = get_formated_number_unit(value)
    return fvalue + unit

def get_file_url(path, rel_path = '', default_path = ''):
    if path.find('/') > 0:
        pure_path = path.split('/')[0] + path.split('.')[-1]
    else:
        pure_path = path
    from config import settings
    if settings['production'] and 'oss_enabled' in settings and settings['oss_enabled']:
        return settings['oss_visit_url'] + pure_path
    elif default_path and not path:
        return default_path
    else:
        return rel_path + path

def query_map_code(db, t):
    if t == 'district':
        res = db.query("select * from dict_district order by district_id ASC")
        lst = [{"id": r.district_id, "name": r.district_name, "type": t, "sid": r.sid, "level": r.i_level} for r in res]
    else:
        res = db.query("select * from t_codes where code_type = %s", t)
        lst = [{"id": r.code_id, "name": r.code_name, "type": r.code_type} for r in res]
    dt = {}
    for l in lst:
        dt[l['id']] = l['name']
    return lst, dt

def init_map_config():
    import torndb
    from config import settings
    db = torndb.Connection(settings['mysql_host'], settings['mysql_database'], settings['mysql_user'], settings['mysql_password'])
    global SIGN_UP_STATUS
    global ASSET_TYPE
    global LAND_TYPE
    global MACHINE_PROPERTY
    global PLANT_PROPERTIES 
    global PROPERTY_ATTRIBUTE
    global STOCK_PROPERTY
    global HOUSE_PROPERTY
    global BANK_CATEGORY
    global DISTRICT_CATEGORY
    global CBRC_TYPE

    global SIGN_UP_STATUS_DICT
    global ASSET_TYPE_DICT
    global LAND_TYPE_DICT
    global MACHINE_PROPERTY_DICT
    global PLANT_PROPERTIES_DICT
    global PROPERTY_ATTRIBUTE_DICT
    global STOCK_PROPERTY_DICT
    global HOUSE_PROPERTY_DICT
    global BANK_CATEGORY_DICT
    global DISTRICT_CATEGORY_DICT
    global CBRC_TYPE_DICT

    SIGN_UP_STATUS, SIGN_UP_STATUS_DICT = query_map_code(db, "sign_up_check")
    # ASSET_TYPE, ASSET_TYPE_DICT = query_map_code(db, "asset_type")
    # LAND_TYPE, LAND_TYPE_DICT = query_map_code(db, "land_type")
    # MACHINE_PROPERTY, MACHINE_PROPERTY_DICT = query_map_code(db, "machine_type")
    # PLANT_PROPERTIES, PLANT_PROPERTIES_DICT = query_map_code(db, "factory_type")
    # PROPERTY_ATTRIBUTE, PROPERTY_ATTRIBUTE_DICT = query_map_code(db, "bizhouse_type")
    # STOCK_PROPERTY, STOCK_PROPERTY_DICT = query_map_code(db, "stock_type")
    # HOUSE_PROPERTY, HOUSE_PROPERTY_DICT = query_map_code(db, "house_type")
    # BANK_CATEGORY, BANK_CATEGORY_DICT = query_map_code(db, "bank_category")
    # DISTRICT_CATEGORY, DISTRICT_CATEGORY_DICT = query_map_code(db, "district")
    # CBRC_TYPE,CBRC_TYPE_DICT = query_map_code(db, "cbrc_type")

    db.close()

# init_map_config()



def get_map_name(t, id):
    m = None
    if t == 'district':
        m = DISTRICT_CATEGORY_DICT
        if id in m:
            res = m[id[:2] + '0000']
            if id[2:4] != '00':
                res += m[id[:4] + '00']
            if id[4:] != '00':
                res += m[id]
            return res
    if t == 'type':
        m = INFO_CATEGORY_DICT
    elif t == 'asset_type':
        m = ASSET_TYPE_DICT
    elif t == 'land_type':
        m = LAND_TYPE_DICT
    elif t == 'machine_type':
        m = MACHINE_PROPERTY_DICT
    elif t == 'factory_type':
        m = PLANT_PROPERTIES_DICT
    elif t == 'bizhouse_type':
        m = PROPERTY_ATTRIBUTE_DICT
    elif t == 'stock_type':
        m = STOCK_PROPERTY_DICT
    elif t == 'house_type':
        m = HOUSE_PROPERTY_DICT
    elif t == 'BANK_CATEGORY_DICT':
        m = BANK_CATEGORY_DICT
    if id in m:
        return m[id]
    return ''

