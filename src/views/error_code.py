#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = 'karldoenitz'

ERROR_CODE = {
    "order_folder_error": {
        "error_code": "150614",
        "error": u"目录操作失败，请检查重试"
    },
    "set_user_name_failed": {
        "error_code": "15064",
        "error": u"设置用户名失败，请稍后重试"
    },
    "reset_failed": {
        "error_code": "15063",
        "error": u"重置失败，请稍后重试"
    },
    "too_many_option": {
        "error_code": "15062",
        "error": u"操作过于频繁，请稍后再试"
    },
    "too_many_regist": {
        "error_code": "15064",
        "error": u"注册次数过多，请换用其他浏览器登录，或于半小时后重新尝试"
    },
    "too_many_login": {
        "error_code": "15061",
        "error": u"登录错误次数过多，请半小时后重新登陆"
    },
    'access_not_exist': {
        "error_code": "404",
        "error": u"请求不存在"
    },
    'access_not_allow': {
        "error_code": "10001",
        "error": u"无权限访问，您可能已经离线，请重新登录"
    },
    'access_need_login': {
        "error_code": "48001",
        "error": u"请先登录，再进行报名和签到"
    },
    'access_need_person_info': {
        "error_code": "48002",
        "error": u"您还未填写个人信息，请完善个人信息，再进行操作"
    },
    'missing_username': {
        # "request": "/rest/user/login",
        "error_code": "10010",
        "error": u"用户名为空"
    },
    'missing_company': {
        # "request": "/rest/user/login",
        "error_code": "10010",
        "error": u"公司名为空"
    },
    'missing_password': {
        # "request": "/rest/user/login",
        "error_code": "10010",
        "error": u"密码为空"
    },
    'missing_new_password': {
        # "request": "/rest/user/login",
        "error_code": "10010",
        "error": u"新密码为空"
    },
    'illegal_password': {
        "error_code": "10011",
        "error": u"密码非法"
    },
    'illegal_new_password': {
        "error_code": "10011",
        "error": u"新密码不合法"
    },
    'illegal_old_password': {
        "error_code": "10011",
        "error": u"旧密码不合法"
    },
    'old_password_error': {
        "error_code": "10011",
        "error": u"原密码错误"
    },
    'password_error': {
        # "request": "/rest/user/login",
        "error_code": "10011",
        "error": u"密码错误"
    },
    'no_user_error': {
        'error_code': '10012',
        'error': u'用户不存在'
    },
    'user_is_exist': {
        'error_code': '10013',
        'error': u'用户已存在'
    },
    'user_is_actived': {
        'error_code': '10013',
        'error': u'用户已激活或者已存在'
    },
    'phone_reg_failed': {
        'error_code': '10014',
        'error': u'校验失败'
    },
    'reset_verify_error': {
        'error_code': '10015',
        'error': u'验证信息缺失'
    },
    'email_active_failed': {
        'error_code': '10016',
        'error': u'邮箱激活失败'
    },
    'error_no_phone': {
        'error_code': '10017',
        'error': u'请填写手机号'
    },
    'error_illegal_phone': {
        'error_code': '10018',
        'error': u'请填写合法的手机号码'
    },
    'error_send_phone_failed': {
        'error_code': '10019',
        'error': u'验证码发送失败'
    },
    'register_failed': {
        'error_code': '10020',
        'error': u'注册失败,请正确填写注册信息'
    },
    'verify_code_error': {
        'error_code': '10021',
        'error': u'验证码错误'
    },
    'verify_code_null': {
        'error_code': '10022',
        'error': u'验证码不能为空'
    },
    'user_not_actived': {
        'error_code': '10023',
        'error': u'用户未激活'
    },
    'user_forbid': {
        'error_code': '10024',
        'error': u'用户已禁用'
    },
    'user_cancel_account': {
        'error_code': '10025',
        'error': u'用户已销户'
    },
    'change_user_info_failed': {
        'error_code': '10026',
        'error': u'用户信息修改失败'
    },
    'no_mail_error': {
        'error_code': '10027',
        'error': u'邮件地址为空'
    },
    'error_illegal_mail': {
        'error_code': '10028',
        'error': u'邮件地址非法'
    },
    'input_error': {
        'error_code': '10029',
        'error': u'输入信息不合法'
    },
    'change_password_error': {
        'error_code': '10030',
        'error': u'密码修改失败'
    },
    'option_error': {
        'error_code': '10031',
        'error': u'操作失败'
    },
    'user_not_login': {
        'error_code': '10032',
        'error': u'用户未登录'
    },
    'no_invite_code': {
        'error_code': '10033',
        'error': u'邀请码错误'
    },
    'not_invalid_invite_code': {
        'error_code': '10034',
        'error': u'邀请码格式非法'
    },
    'used_invite_code': {
        'error_code': '10035',
        'error': u'邀请码已被使用'
    },
    'non_invite_code': {
        'error_code': '10036',
        'error': u'邀请码为空'
    },
    'file_too_large': {
        'error_code': '10037',
        'error': u'文件过大'
    },
    'file_type_error': {
        'error_code': '10038',
        'error': u'文件类型错误'
    },
    'file_write_error': {
        'error_code': '10039',
        'error': u'抱歉，文件写入错误'
    },
    'file_not_exist': {
        'error_code': '100391',
        'error': u'文件不存在或者没有权限下载'
    },
    'file_not_allow': {
        'error_code': '100392',
        'error': u'文件不存在或者没有权限使用'
    },
    'update_user_card_failed': {
        'error_code': '10040',
        'error': u'更新名片失败'
    },
    'order_miss_id': {
        'error_code': '60001',
        'error': u'缺少订单ID'
    },
    'order_non_exist': {
        'error_code': '60002',
        'error': u'订单不存在'
    },
    'order_miss_param': {
        'error_code': '60003',
        'error': u'缺少参数, 无法提交订单'
    },
    'order_file_not_coexisting': {
        'error_code': '60003',
        'error': u'一个订单中不能同时包含Excel文件和PDF图片'
    },
    'order_miss_data': {
        'error_code': '60004',
        'error': u"订单未提交"
    },
    'order_no_file': {
        'error_code': '60005',
        'error': u'没有上传文件'
    },
    'order_invalid_confirm': {
        'error_code': '60006',
        'error': u'订单状态不允许再次确认报表数据'
    },
    'order_miss_code': {
        'error_code': '60007',
         'error': u'缺少订单号'
    },
    'order_miss_product': {
        'error_code': '60009',
         'error': u'没有选择产品'
    },
    'order_tab_not_exists': {
        'error_code': '600091',
         'error': u'没有该结果类型'
    },
    'order_tab_not_allow': {
        'error_code': '600092',
         'error': u'没有权限获取该结果数据'
    },
    'account_not_enough': {
        'error_code': '60100',
        'error': u'账户余额不足，请及时充值'
    },
    'order_parse_error': {
        'error_code': '60101',
        'error': u'报表格式不规范, 不能识别'
    },
    'order_invalid_pay': {
        'error_code': '601011',
        'error': u'订单当前状态不能支付，请联系管理员'
    },
    'order_invalid_pricing': {
        'error_code': '601012',
        'error': u'订单订单划价出错，请检查重试'
    },
    'order_pay_update_error': {
        'error_code': '601013',
        'error': u'订单支付成功，但记账失败，请联系客服'
    },
    'order_undo_payment_error': {
        'error_code': '60102',
        'error': u'订单退费失败, 请联系管理员'
    },
    'order_uncompleted': {
        'error_code': '60103',
        'error': u'订单未完成或者结果不能被查看'
    },
    'order_not_cancel': {
        'error_code': '60103',
        'error': u'订单不能被取消'
    },
    'order_cancel_fail': {
        'error_code': '60104',
        'error': u'订单取消操作失败'
    },
    'order_submit_frequent': {
        'error_code': '60103',
        'error': u'提交订单太频繁，请稍候再提交'
    },
    'order_sample_exists': {
        'error_code': '60104',
        'error': u'样本报表已存在'
    },
    "order_is_working": {
        "error_code": "12580",
        "error": u"系统繁忙处理中，请稍候..."
    },
    'miss_param': {
        'error_code': '60103',
        'error': u'缺少参数'
    },
    'no_user_code': {
        'error_code': "60104",
        'error': u"未设置用户名"
    },
    'is_slave_user': {
        'error_code': "60105",
        'error': u"您已是子用户，不能再添加子用户"
    },
    'download_permission_deny': {
        'error_code': "60200",
        'error': u"没有权限下载"
    },
    'order_unfinished_download_permission_deny': {
        'error_code': "60201",
        'error': u"订单未成功,无法下载!"
    },
    'stock_code_error': {
        'error_code': "60202",
        'error': u"上市公司代码不存在! 目前上市公司查询只包括沪深股市一般企业，暂未覆盖银行、保险等金融企业"
    },
    'stock_not_login_limited': {
        'error_code': "60202",
        'error': u"非注册用户每天只能查5个上市公司! 请先注册并登录，即可随便查询！"
    },
    #----info for manager --#
    'mgr_no_login': {
        'error_code': '5000',
        'error': u'未登录！',
    },
    'mgr_login_succ': {
        'error_code': '5001',
        'mgr_code': '',
        'error': u'管理员登录成功！'
    },
    'mgr_login_fail': {
        'error_code': '5002',
        'error': u'用户名或密码错误！',
    },
    'mgr_login_deny': {
        'error_code': '5003',
        'error': u'禁止登录！'
    },
    'mgr_modify_old_pwd_err': {
        'error_code': '5004',
        'error': u'原密码不正确！',
    },
    'mgr_modify_new_pwd_err': {
        'error_code': '5005',
        'error': u'新密码不正确！',
    },
    'mgr_pwd_err': {
        'error_code': '5006',
        'error': u'密码不正确！'
    },
    'mgr_code_err': {
        'error_code': '5007',
        'error': u'管理员账号不正确！'
    },
    'mgr_action_deny': {
        'error_code': '5008',
        'error': u'无权限执行此操作！'
    },
    'mgr_role_empty': {
        'error_code': '5009',
        'error': u'角色ID为空！'
    },
    'mgr_code_empty': {
        'error_code': '5010',
        'error': u'管理员账户为空！'
    },
    'mgr_auth_fail': {
        'error_code': '5011',
        'error': u'授权失败'
    },
    'mgr_add_fail': {
        'error_code': '5012',
        'error': u'添加管理员失败'
    },
    'mgr_update_fail': {
        'error_code': '5013',
        'error': u'更新管理员失败'
    },

    #-------for products----
    'empty_products': {
        'error_code': '6001',
        'error': u'没有产品数据'
    },
    "product_id_empty": {
        "error_code": '6002',
        "error": u"产品ID为空"
    },
    "product_name_invalid": {
        "error_code": '6003',
        "error": u"产品名称不合法"
    },
    "product_price_invalid": {
        "error_code": '6004',
        "error": u"价格不合法",
    },
    "product_status_invalid": {
        "error_code": '6005',
        'error': u'产品状态不合法'
    },
    "product_add_fail": {
        "error_code": '6006',
        'error': u'添加产品失败'
    },
    "product_not_exist": {
        "error_code": '6007',
        'error': u'产品不存在或者已经下架'
    },

    "policy_not_exist": {
        "error_code": '6007',
        'error': u'优惠不存在'
    },

    'biz_cost_none': {
        "error_code": '9001',
        "error": u'账户没有消费记录'
    },
    'biz_asset_none': {
        "error_code": '9002',
        "error": u'账户没有资产记录'
    },
    'biz_account_refresh_error': {
        "error_code": '9003',
        "error": u'账户刷新失败'
    },
    'biz_account_not_exist': {
        "error_code": '9004',
        "error": u'账户不存在'
    },
    'biz_asset_add_error': {
        "error_code": '9005',
        "error": u'账户账本充值出错'
    },
    'biz_cash_recharge_error': {
        "error_code": '9006',
        "error": u'账户现金充值出错'
    },

    'add_child_failed': {
        "error_code": '9106',
        "error": u'子账户添加失败'
    },
    'child_no_child': {
        "error_code": '9107',
        "error": u'子账户不能添加子账户'
    },
    'child_no_parent_name': {
        "error_code": '9108',
        "error": u'请先设置用户名, 再添加子账户'
    },
    'child_coin_0_error': {
        "error_code": '9109',
        "error": u'限额不能为零'
    },
    'child_invalid_parent': {
        "error_code": '9110',
        "error": u'当前子账户不能被删除, 请确定你是真实的父账户'
    },
    'child_delete_error': {
        "error_code": '9111',
        "error": u'删除子账户出错!'
    },
    'child_switch_error': {
        "error_code": '9112',
        "error": u'切换到账户出错!'
    },
    'child_relation_error': {
        "error_code": '9113',
        "error": u'账户关系不存在!'
    },
    'child_not_support': {
        "error_code": '9114',
        "error": u'您所在的用户级别不允许创建子账户'
    },

    #--------- for rest.py ------
    "order_file_invalid": {
        "error_code": "80001",
        "error": u'文件类型不合法（只允许xls|xlsx|pdf）'
    },
    "short_url_timeout": {
        "error_code": "80002",
        "error": u"分享地址已经过期"
    },
    "short_url_error": {
        "error_code": "80003",
        "error": u"分享地址生成失败"
    },
    "no_slected_payment": {
        "error_code": "8020",
        "error": u"未选择支付方式"
    },
    "recharge_error": {
        "error_code": "8021",
        "error": u'充值失败'
    },
    "recharge_create_error":{
        "error_code": "8022",
        "error": u'新建充值订单失败'
    },

    "sheet_compose_non_editable":{
        "error_code": "8022",
        "error": u'任务已经完成或者正在评估，不能再修改'
    },
    "sheet_compose_join_failed":{
        "error_code": "8022",
        "error": u'任务创建失败'
    },
    "sheet_compose_not_allow":{
        "error_code": "8022",
        "error": u'没有权限处理任务'
    },

    "redpack_duplicated":{
        "error_code": "8022",
        "error": u'红包已经领过啦！'
    },
    "redpack_not_exist":{
        "error_code": "8022",
        "error": u'红包已经过期啦！下次再来抢吧！'
    },
    "redpack_error":{
        "error_code": "8022",
        "error": u'红包领取出错！'
    },
    "invoice_unable": {
        "error_code": "15062",
        "error": u"出错了：可开发票金额不足"
    },         

}



