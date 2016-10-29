# -*- coding:utf-8 -*-
'''
说明：本工模块提供常用到几个方法
创建日期：2015-02-03
修改日期：
''' 
import copy   
def model_get_max(*v,**vl): 
    '''
    取输入值的最大值
    '''
    if len(v)==0:
        return None
    v_return =v[0]
    for i in v: 
        if i>v_return:
            v_return =i
    return v_return
    pass

def model_get_min(*v,**vl): 
    '''
        取输入值的最小值
    '''
    if len(v)==0:
        return None
    v_return =v[0]
    for i in v: 
        if i<v_return:
            v_return =i
    return v_return
    pass 

def model_get_min2(base_data,*v,**vl): 
    '''
        取输入值的最距离的值
    ''' 
    if len(v)==0:
        return None
    v_return =float(v[0] )
    v_tmp=abs(float(v[0])- float(base_data))
    for i in v:   
        if abs(float(i)-float(base_data))<v_tmp:
            v_return =float(i)
            v_tmp=abs(float(i)- float(base_data))  
    return v_return
    pass 
'''
取模型结果
创建日期：2015-02-03
参数：v
{
    "s_a1":0.00,#--原始的收入
    "s_a2":0.00,#--原始的成本
    "s_a3":0.00,#--原始的费用
    "a1":0.00,#--曹老师估算的收入
    "a2":0.00,#--曹老师估算的成本
    "a3":0.00,#--曹老师估算的费用
    "sr":0.00,#--吴老师估算的收入
    "cb":0.00,#--吴老师估算的成本
    "fy":0.00,#--吴老师估算的费用
    "cash_revu_gap":0.00,#
    "ngc_real_val":0.00,#
    "chi":0.00,#
    "neg":0.00,#
}
'''
def __geric_result(v):
    '''
        生成区间，v为一个数值
    '''
    ent_result={"ubound":None,"lbound":None}
    if v==None:
        return ent_result
    if v>1000000:
        ent_result["ubound"]=v*0.9
        ent_result["lbound"]=v*1.1
    elif v>400000:
        ent_result["ubound"]=v*0.88
        ent_result["lbound"]=v*1.12
    elif v>50000:
        ent_result["ubound"]=v*0.85
        ent_result["lbound"]=v*1.15
    else: 
        ent_result["ubound"]=v*0.8
        ent_result["lbound"]=v*1.2 

    return ent_result
    pass
# 此方法当前弃用 2015-02-06
def model_get_result(v):

    if type(v)!=dict:
        return None


    ent_return ={
        "ubound":None, #上限值
        "value" :None, #计算值
        "lbound":None  #下限值
    }
    ratio_sr=0.35
    ratio_cb=0.50
    ratio_fy=0.15

    #合并原值
    l_sr = v["s_a1"]*ratio_sr + v["s_a2"]*ratio_cb + v["s_a3"]*ratio_fy

    #合并估算值
    l_gusuan1 = v["a1"]  * ratio_sr + v["a2"]  *ratio_cb + v["a3"]  *ratio_fy
    l_gusuan2 = v["sr"]*ratio_sr + v["cb"] *ratio_cb + v["fy"]  *ratio_fy
    #求差额
    l_lrce = model_get_min( abs(l_gusuan2-l_sr) ,abs(l_gusuan1 - l_sr)) 
    
    #比率计算
    if l_sr==0:
        return None
    l_temp = l_lrce /l_sr 

    #第一次调整
    if l_temp>=0.5 or (l_lrce<=1000000 and l_lrce>100000 and v["chi"]<=15):
        if abs(v["cash_revu_gap"])>0  and abs(v["ngc_real_val"])>0 :
            l_lrce=model_get_min(l_lrce,abs(v["cash_revu_gap"]),abs(v["ngc_real_val"]))
        else:
            if abs(v["cash_revu_gap"])>0:
                l_lrce=model_get_min(l_lrce,abs(v["cash_revu_gap"])) 

            if abs(v["ngc_real_val"])>0 :
                l_lrce=model_get_min(l_lrce,abs(v["ngc_real_val"]))


    #准备第二次调整
    l_temp = l_lrce /l_sr 
    if l_temp>=0.5 :
        l_lrce =l_sr *0.5


    #最后一次调整
    if v["chi"]<=10 and abs(v["neg"])<=0.05 :
        l_lrce=model_get_min(l_lrce,abs(v["ngc_real_val"])) 

    ent_return["value"] =l_lrce
    tmp_v = __geric_result(l_lrce)
    ent_return["ubound"] =tmp_v["ubound"]
    ent_return["lbound"] =tmp_v["lbound"]
    return ent_return
    pass
def rst_comprehensive(conn,order_id):
    ent_list=[]
    ent_return={"success":False,"message":""}
    # ent_list =_rst_query_data(conn,order_id)
    # _rst_generic(ent_list) 
    # _save2db(conn,ent_list)
    try:
        ent_list =_rst_query_data(conn,order_id)
        _rst_generic(ent_list)
        _save2db(conn,ent_list)
        ent_return["success"]=True
    except Exception,e: 
        ent_return["message"]=e
    ent_return["module"]="rst_comprehensive(conn,order_id)"
    return ent_return
    pass
# 保存的操作
def _save2db(conn,ent_list):
    sql_template='''
        insert into rst_final_models(
             firm_code,por,dt_property,dt_type,dt_source,order_id,rfm_a1_old,rfm_a2_old,rfm_a3_old,rfm_a1,rfm_a2,rfm_a3,rfm_revenue,rfm_cost,rfm_exp,rfm_asien_revenue,rfm_asien_cost,rfm_asien_exp,rfm_p1,rfm_p2,rfm_p3,rfm_profit,rfm_profit_ubound,rfm_profit_lbound,rfm_content
            ) values(
             '%s','%s','%s','%s','%s','%s',%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'');
    ''' 
    arr4save=[]
    arr_keys={}
    temp_arr=[]
    for v in ent_list:
        temp_arr=[]
        temp_arr.append(v["firm_code"]);
        temp_arr.append(v["por"]);
        temp_arr.append(v["dt_property"]);
        temp_arr.append(v["dt_type"]);
        temp_arr.append(v["dt_source"]);
        temp_arr.append(v["order_id"]);
        temp_arr.append(v["rfm_a1_old"]);
        temp_arr.append(v["rfm_a2_old"]);
        temp_arr.append(v["rfm_a3_old"]);
        temp_arr.append(v["rfm_a1"]);
        temp_arr.append(v["rfm_a2"]);
        temp_arr.append(v["rfm_a3"]);
        temp_arr.append(v["rfm_revenue"]);
        temp_arr.append(v["rfm_cost"]);
        temp_arr.append(v["rfm_exp"]);
        temp_arr.append(v["rfm_asien_revenue"]);
        temp_arr.append(v["rfm_asien_cost"]);
        temp_arr.append(v["rfm_asien_exp"]);
        temp_arr.append(v["rfm_p1"]);
        temp_arr.append(v["rfm_p2"]);
        temp_arr.append(v["rfm_p3"]);
        temp_arr.append(v["rfm_profit"]);
        temp_arr.append(v["rfm_profit_ubound"]);
        temp_arr.append(v["rfm_profit_lbound"]);
        # temp_arr.append(v["rfm_content"]);  
        tt_tuple = tuple(temp_arr)
        arr_keys[v["order_id"]]=None
        # print 'abcde',tt_tuple
        arr4save.append(sql_template % tt_tuple)
        pass
    if len(arr4save)>0:
        for key in arr_keys.keys(): 
            # arr4save.insert(0,"delete from rst_final_models where order_id='%s';" % key )
            conn.execute("delete from rst_final_models where order_id='%s';" % key )
        for v in arr4save: 
            conn.execute(v)
        pass
    pass
def _rst_query_data(conn,order_id):
    sql_template='''
        select 
            t2.firm_code,
            t2.por,
            t2.dt_source,
            t2.dt_property, 
            t2.order_id,
            t2.dt_type,
            ifnull(pa100t_op_revenue,0) rfm_a1_old,
            ifnull(pa200t_op_cost,0) rfm_a2_old,
            ifnull(pa22010_sales_exp,0) + ifnull(pa22020_admin_exp,0) + ifnull(pa22030_fin_exp,0) rfm_a3_old,
            ngc_id_neg_other,
            ngc_gap_revenue,
            ngc_gap_revenue_inc,
            ngc_cf_tag,
            ngc_gap_cash,
            ngc_gap_absolute_cash,
            id_neg_other,
            ngc_real_val,
            cash_revu_gap,
            cash_revu_gap_cf,
            main_revenue_evaluated,
            main_cost_evaluated,
            main_revenue_evmax,
            main_cost_evmax,
            main_revenue_evmin1,
            main_cost_evmin1,
            main_revenue_evmin2,
            main_cost_evmin2,
            main_revenue_evmin2 rfm_asien_revenue,
            main_cost_evaluated rfm_asien_cost,
            expense_ev+main_cost_evmin2-main_cost_evaluated rfm_asien_exp,
            expense_ev,
            expense_ev_se01,
            expense_ev_se02,
            expense_ev_se03,
            tc_a1 rfm_a1,
            tc_a2 rfm_a2,
            tc_a3 rfm_a3,
            tc_a4,
            tc_a5,
            tc_a6,
            tc_a7,
            tc_a8,
            tc_a9,
            tc_a10,
            stat_revenue rfm_revenue,
            stat_cost rfm_cost,
            stat_exp rfm_exp
            from bd_common_bs t1,bd_common_pl t2 , rst_negcash t3, rst_stat_model t4 , rst_tc t5
            where t1.order_id =t2.order_id
                  and t1.por =t2.por
                    and t1.dt_type =t2.dt_type
                  and t1.order_id =t3.order_id
                  and t1.por =t3.por
                    and t1.dt_type =t3.dt_type
                  and t1.order_id =t4.order_id
                  and t1.por =t4.por
                    and t1.dt_type =t4.dt_type
                  and t1.order_id =t5.order_id
                  and t1.por =t5.por
                    and t1.dt_type =t5.dt_type 
                  and t2.dt_property =t4.dt_property
                  and t2.dt_property =t5.dt_property
                  and t1.dt_property =1
                  and t1.order_id ='%s' 
                  order by t1.por
    '''
    ent_list=[]
    # print sql_template % order_id
    dt_table =conn.query(sql_template % order_id)
    for row in dt_table: 
        temp_ent={}
        temp_ent["firm_code"]=str(row["firm_code"])
        temp_ent["por"]=  str(row["por"])
        temp_ent["dt_property"]=str(row["dt_property"])
        temp_ent["dt_type"]=str(row["dt_type"])
        temp_ent["dt_source"]=str(row["dt_source"])
        temp_ent["order_id"]=str(row["order_id"])
        temp_ent["rfm_a1_old"]=str(row["rfm_a1_old"])
        temp_ent["rfm_a2_old"]=str(row["rfm_a2_old"])
        temp_ent["rfm_a3_old"]=str(row["rfm_a3_old"])
        temp_ent["rfm_a1"]=str(row["rfm_a1"])
        temp_ent["rfm_a2"]=str(row["rfm_a2"])
        temp_ent["rfm_a3"]=str(row["rfm_a3"])
        temp_ent["rfm_revenue"]=str(row["rfm_revenue"])
        temp_ent["rfm_cost"]=str(row["rfm_cost"])
        temp_ent["rfm_exp"]=str(row["rfm_exp"])
        temp_ent["rfm_asien_revenue"]=str(row["rfm_asien_revenue"])
        temp_ent["rfm_asien_cost"]=str(row["rfm_asien_cost"])
        temp_ent["rfm_asien_exp"]=str(row["rfm_asien_exp"])
        temp_ent["rfm_p1"]=0
        temp_ent["rfm_p2"]=0
        temp_ent["rfm_p3"]=0
        temp_ent["rfm_profit"]=0
        temp_ent["rfm_profit_ubound"]=0
        temp_ent["rfm_profit_lbound"]=0
        temp_ent["rfm_content"]=0

        ent_list.append(temp_ent) 
    return ent_list
    pass
# 结果的综合处理
def _rst_generic(v_ent):
    '''
        v_ent=[
        {
            "firm_code":None, #企业代码
            "por":None, #所属期
            "dt_property":None, #数据属性标志
            "dt_type":None, #数据类型
            "dt_source":None, #数据来源
            "order_id":None, #订单号
            "rfm_a1_old":None, #申报收入
            "rfm_a2_old":None, #申报成本
            "rfm_a3_old":None, #申报费用
            "rfm_a1":None, #曹老师估算收入
            "rfm_a2":None, #曹老师估算成本
            "rfm_a3":None, #曹老师估算费用
            "rfm_revenue":None, #吴老师估算收入
            "rfm_cost":None, #吴老师估算成本
            "rfm_exp":None, #吴老师估算费用
            "rfm_asien_revenue":None, #陈博士估算收入
            "rfm_asien_cost":None, #陈博士估算成本
            "rfm_asien_exp":None, #陈博士估算费用
            "rfm_p1":None, #整理后的收入
            "rfm_p2":None, #整理后的成本
            "rfm_p3":None, #整理后的费用
            "rfm_profit":None, #利润差额
            "rfm_profit_ubound":None, #利润差额上限
            "rfm_profit_lbound":None, #利润差额下限
            "rfm_content":None,#描述信息
            }
        ] 
    '''
    ent_result={"success":False,"message":""}

    try:
        i_loop =0
        i_count =0
        i_count =len(v_ent)
        for i_loop in range(0,i_count): 
            v=v_ent[i_loop] 
            min_sr=model_get_min2(v["rfm_a1_old"] ,v["rfm_a1"],v["rfm_revenue"],v["rfm_asien_revenue"])
            min_cb=model_get_min2(v["rfm_a2_old"] ,v["rfm_a2"],v["rfm_cost"],v["rfm_asien_cost"])
            min_fy=model_get_min2(v["rfm_a3_old"] ,v["rfm_a3"],v["rfm_exp"],v["rfm_asien_exp"])
            # print i_loop
            v["rfm_p1"]=min_sr-float(v["rfm_a1_old"])
            v["rfm_p2"]=min_cb-float(v["rfm_a2_old"])
            v["rfm_p3"]=min_fy-float(v["rfm_a3_old"])

            # 利润差额
            ubound=0
            lbound=0
            v["rfm_profit"]= float(v["rfm_p1"]) - float(v["rfm_p2"]) -float(v["rfm_p3"])   #float(v["rfm_p1"]) -float(v["rfm_a1"])- float(v["rfm_p2"]) +float(v["rfm_a2"]) - float(v["rfm_p3"]) + float(v["rfm_a3"])
            if v["rfm_profit"]>1000000:
                bound1=float(v["rfm_profit"])*0.9 
                bound2=float(v["rfm_profit"])*1.1
                pass
            elif v["rfm_profit"]>400000:
                bound1=float(v["rfm_profit"])*0.88 
                bound2=float(v["rfm_profit"])*1.12
                pass
            elif v["rfm_profit"]>50000:
                bound1=float(v["rfm_profit"])*0.85 
                bound2=float(v["rfm_profit"])*1.15
                pass
            else:
                bound1=float(v["rfm_profit"])*0.8 
                bound2=float(v["rfm_profit"])*1.2
                pass

            if bound1>bound2:
                ubound=bound1
                lbound=bound2
            else: 
                ubound=bound2
                lbound=bound1
            v["rfm_profit_ubound"]=ubound
            v["rfm_profit_lbound"]=lbound  
        ent_result["success"]=True
        pass
    except Exception ,e:
        ent_result["message"]=e
        pass

    return ent_result
    pass
def test():
    vv={
        "s_a1":10.00,#--原始的收入
        "s_a2":10.00,#--原始的成本
        "s_a3":20.00,#--原始的费用
        "a1":30.00,#--曹老师估算的收入
        "a2":40.00,#--曹老师估算的成本
        "a3":50.00,#--曹老师估算的费用
        "sr":60.00,#--吴老师估算的收入
        "cb":70.00,#--吴老师估算的成本
        "fy":80.00,#--吴老师估算的费用
        "cash_revu_gap":10.00,#
        "ngc_real_val":10.00,#
        "chi":10.00,#
        "neg":10.00,#
    }
    # print model_get_result(vv)
    pass
# test()
def tttt():  
    import torndb 
    db = torndb.Connection("192.168.1.128", "asien", "root", "123456")  
    print rst_comprehensive(db,'a8ac9ae2-9d45-11e4-9a97-080027823c9a')
    pass
# tttt()
 