# -*- coding:utf-8 -*-

# 测试mysql无记录时，返回的是什么
import tornado.gen


@tornado.gen.coroutine
def _get_por(v_order_id, conn):
    result_ent = {}
    str_sql ="select DISTINCT concat(year(por) -1,'') as por from bd_common_bs  where order_id ='%s'"
    a_result = yield conn.query(str_sql % v_order_id)
    for v in a_result: 
        result_ent[v["por"]] = {}
    # print result_ent
    raise tornado.gen.Return(result_ent or {})


@tornado.gen.coroutine
def _get_std_detail(conn, whereclause, industry_id):
    str_sql = "select * from bd_ratio_std  where por in (%s) and industry_id='%s'" % (whereclause, industry_id)
    result = yield conn.query(str_sql)
    raise tornado.gen.Return(result or [])


@tornado.gen.coroutine
def get_ratio_std(conn, v_order_id, industry_id):
    result_por = yield _get_por(v_order_id, conn)
    v_keys = result_por.keys()
    v_pors = ','.join("'%s-12-31'" % a for a in v_keys)
    result_std = yield _get_std_detail(conn, v_pors, industry_id)
    i_count = len(result_std)
    for i_loop in range(0, i_count):
        v = result_std[i_loop]
        s_year = str(v["por"].year)
        ent = result_por[s_year]
        s_item = v["item_name"]
        if "item_name" in v:
            del v["item_name"]
        if "por" in v:
            del v["por"]
        if "industry_id" in v:
            del v["industry_id"]
        ent[s_item] = v
    raise tornado.gen.Return(result_por or {})


@tornado.gen.coroutine
def get_ratio_std_result(order_id, industry_id, conn):
    result = yield get_ratio_std(conn, order_id, industry_id)
    raise tornado.gen.Return(result)


# def test():
#     result = get_ratio_std_result("7cf8d550-73b5-11e4-83e6-60d8194fce1f", "10")
#     print result
#
#
# test()