# -*- coding: utf-8 -*-  

import os
import views.uimodules as uimodules


settings = {

    # app lists
    "apps": [
        {
            # 应用唯一号
            "app_id": "fudan",
            # mysql 主服务器IP
            "mysql_host": '127.0.0.1',
            # mysql 从服务器IP
            "mysql_host_slaves": ['127.0.0.1'], 
            # mysql 端口号
            "mysql_port": 3306,
            # mysql 用户名
            "mysql_user": 'root',
            # mysql 密码
            "mysql_password": "sogou",
            # mysql 数据库名
            "mysql_database": "pay_it",
            "mysql_max_conn": 10,
            # mysql 字符编码
            "mysql_charset": "utf8",
        }
    ],

    # 应用唯一号
    # "app_id": "marsapp",

    # 静态文件目录
    "static_path": os.path.join(os.path.dirname(__file__), "static/"),

    # 模板文件目录
    "template_path": os.path.join(os.path.dirname(__file__), "tpl/"),

    # cookie加密串
    "cookie_secret": "!dkie~`-=+lwlek121231312**&78381212@@1!#.~~~",

    # UI Modules组件
    "ui_modules": uimodules,

    # 跨域访问cookie开关
    "xsrf_cookies": False,

    # Redis的session加密串
    'session_secret': "3cdcb1f00803b6e78ab50b466a40b9977db396840c28307f428b25e2277f1bcc",

    # Redis session的过期时间(单位：秒)， 默认为30分钟
    'session_timeout': 1800, 

    # Redis 服务器配置
    'store_options': {
        'redis_host': '127.0.0.1',#'192.168.180.160', 
        'redis_port': 6379, 
        'redis_pass': ''
    }, 

    # 用户密码加密密钥 the length can be (16, 24, 32)
    'cipher': 'ot-$7Y0z(WH=3l>re_XC|t0?%T^Ka|dd', 

    # 是否debug
    'debug': False,

    # 是否生产环境
    'production': True,

    # 设置文件保存目录
    "original_file_path": "/var/marsfile-sheets/",

    # 阿里云OSS配置
    "oss_enabled": False,
    "oss_bucket_name": "zyyp-abc",
    "oss_endpoint": "oss-cn-abc.com",
    "oss_accessKeyId": "jaja",
    "oss_accessKeySecret": "1111",
    "oss_visit_url": "http://zyyp-zjabank.abc.com/",

    # 识读校验和OCR通知邮箱
    "worker_mail": ['chengquan.li@tsingdata.com'],

}
