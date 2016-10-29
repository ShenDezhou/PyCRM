# -*- coding: utf-8 -*-  
import json, os

from lib import asynctorndb

PAGES = json.loads(open(os.path.join(os.path.dirname(__file__), "constants/pages.json"), "rb").read())

MGR_PAGES = json.loads(open(os.path.join(os.path.dirname(__file__), "constants/mgr_pages.json"), "rb").read())

COMMON_PAGES = json.loads(open(os.path.join(os.path.dirname(__file__), "constants/common_pages.json"), "rb").read())

BODY_PAGES = []

LOGIN_PAGES = json.loads(open(os.path.join(os.path.dirname(__file__), "constants/mgr_unauth.json"), "rb").read())
