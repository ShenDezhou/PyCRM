# -*-coding:utf-8 -*-
'''
用于处理模型最终结果用
创建日期：2015-05-20
说明：
    此方法不涉及数据的读取与保存

修改日期：2015-06-09
修改原因：由于企业不一定有现金流量表，为了规避单个项目为0的问题，
          特意修改处理。 
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
        if i!=0:
            v_return =i
            break
    if v_return ==0:
        return -1

    for i in v: 
        if abs(i)< abs(v_return) and i!=0:
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



# 结果的综合处理
def rst_generic(v_ent):
    ''' 
        v_ent=[
        {
            "firm_code":None, #企业代码
            "por":None, #所属期
            "dt_property":None, #数据属性标志
            "dt_type":None, #数据类型
            "dt_source":None, #数据来源
            "order_id":None, #订单号
            "rfm_a1_old":None, #申报收入  pa100t_op_revenue
            "rfm_a2_old":None, #申报成本 pa200t_op_cost
            "rfm_a3_old":None, #申报费用  pa22010_sales_exp +  pa22020_admin_exp+  pa22030_fin_exp
            "rfm_a1":None, #曹老师估算收入
            "rfm_a2":None, #曹老师估算成本
            "rfm_a3":None, #曹老师估算费用
            "rfm_revenue":None, #吴老师估算收入
            "rfm_cost":None, #吴老师估算成本
            "rfm_exp":None, #吴老师估算费用
            "rfm_asien_revenue":None, #陈博士估算收入 main_revenue_evmin2
            "rfm_asien_cost":None, #陈博士估算成本  main_cost_evaluated  
            "rfm_asien_exp":None, #陈博士估算费用 expense_ev+main_cost_evmin2-main_cost_evaluated  
            "rfm_p1":None, #整理后的收入差额 ，保存临时值用
            "rfm_pl_ubound":None ,
            "rfm_pl_lbound":None ,
            "rfm_p2":None, #整理后的成本差额  ，保存临时值用
            "rfm_p2_ubound":None ,
            "rfm_p2_lbound":None ,
            "rfm_p3":None, #整理后的费用差额 ，保存临时值用 
            "rfm_p3_ubound":None ,
            "rfm_p3_lbound":None ,
            "rfm_profit":None, #利润差额 ，保存临时值用
            "rfm_profit_ubound":None, #利润差额上限 ，保存临时值用
            "rfm_profit_lbound":None, #利润差额下限 ，保存临时值用
            "rfm_content":None,#描述信息 
            "cf_flag":0 , # 0:没有，1：有现金流量表
            ""
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
            v["rfm_profit"]= float(v["rfm_p1"]) - float(v["rfm_p2"]) -float(v["rfm_p3"])
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

            # 收入差额上下限
            ubound=0
            lbound=0
            if v["rfm_p1"]>1000000:
                bound1=float(v["rfm_p1"])*0.9 
                bound2=float(v["rfm_p1"])*1.1
                pass
            elif v["rfm_p1"]>400000:
                bound1=float(v["rfm_p1"])*0.88 
                bound2=float(v["rfm_p1"])*1.12
                pass
            elif v["rfm_p1"]>50000:
                bound1=float(v["rfm_p1"])*0.85 
                bound2=float(v["rfm_p1"])*1.15
                pass
            else:
                bound1=float(v["rfm_p1"])*0.8 
                bound2=float(v["rfm_p1"])*1.2
                pass

            if bound1>bound2:
                ubound=bound1
                lbound=bound2
            else: 
                ubound=bound2
                lbound=bound1
            v["rfm_p1_ubound"]=ubound
            v["rfm_p1_lbound"]=lbound  

            # 成本差额上下限
            ubound=0
            lbound=0
            if v["rfm_p2"]>1000000:
                bound1=float(v["rfm_p2"])*0.9 
                bound2=float(v["rfm_p2"])*1.1
                pass
            elif v["rfm_p2"]>400000:
                bound1=float(v["rfm_p2"])*0.88 
                bound2=float(v["rfm_p2"])*1.12
                pass
            elif v["rfm_p2"]>50000:
                bound1=float(v["rfm_p2"])*0.85 
                bound2=float(v["rfm_p2"])*1.15
                pass
            else:
                bound1=float(v["rfm_p2"])*0.8 
                bound2=float(v["rfm_p2"])*1.2
                pass

            if bound1>bound2:
                ubound=bound1
                lbound=bound2
            else: 
                ubound=bound2
                lbound=bound1
            v["rfm_p2_ubound"]=ubound
            v["rfm_p2_lbound"]=lbound 

            # 费用差额上下限
            ubound=0
            lbound=0
            if v["rfm_p3"]>1000000:
                bound1=float(v["rfm_p3"])*0.9 
                bound2=float(v["rfm_p3"])*1.1
                pass
            elif v["rfm_p3"]>400000:
                bound1=float(v["rfm_p3"])*0.88 
                bound2=float(v["rfm_p3"])*1.12
                pass
            elif v["rfm_p3"]>50000:
                bound1=float(v["rfm_p3"])*0.85 
                bound2=float(v["rfm_p3"])*1.15
                pass
            else:
                bound1=float(v["rfm_p3"])*0.8 
                bound2=float(v["rfm_p3"])*1.2
                pass

            if bound1>bound2:
                ubound=bound1
                lbound=bound2
            else: 
                ubound=bound2
                lbound=bound1
            v["rfm_p3_ubound"]=ubound
            v["rfm_p3_lbound"]=lbound 
        ent_result["success"]=True
        pass
    except Exception ,e:
        ent_result["message"]=e
        pass

    return ent_result
    pass 

# 结果的综合处理,2015-06-09添加，
# 由于需要整合的输入增加了，所以特意添加了这个方法。
def rst_generic2(v_ent):
    ''' 
        v_ent=[
        {
            "firm_code":None, #企业代码
            "por":None, #所属期
            "dt_property":None, #数据属性标志
            "dt_type":None, #数据类型
            "dt_source":None, #数据来源
            "order_id":None, #订单号
            "rfm_a1_old":None, #申报收入  pa100t_op_revenue
            "rfm_a2_old":None, #申报成本 pa200t_op_cost
            "rfm_a3_old":None, #申报费用  pa22010_sales_exp +  pa22020_admin_exp+  pa22030_fin_exp
            "rfm_a1":None, #曹老师估算收入
            "rfm_a2":None, #曹老师估算成本
            "rfm_a3":None, #曹老师估算费用
            "rfm_revenue":None, #吴老师估算收入
            "rfm_cost":None, #吴老师估算成本
            "rfm_exp":None, #吴老师估算费用
            "rfm_asien_revenue":None, #陈博士估算收入 main_revenue_evmin2
            "rfm_asien_cost":None, #陈博士估算成本  main_cost_evaluated  
            "rfm_asien_exp":None, #陈博士估算费用 expense_ev+main_cost_evmin2-main_cost_evaluated  
            "rfm_p1":None, #整理后的收入
            "rfm_pl_ubound":None ,
            "rfm_pl_lbound":None ,
            "rfm_p2":None, #整理后的成本
            "rfm_p2_ubound":None ,
            "rfm_p2_lbound":None ,
            "rfm_p3":None, #整理后的费用 
            "rfm_p3_ubound":None ,
            "rfm_p3_lbound":None ,
            "rfm_profit":None, #利润差额 ，保存临时值用
            "rfm_profit_ubound":None, #利润差额上限 ，保存临时值用
            "rfm_profit_lbound":None, #利润差额下限 ，保存临时值用
            "rfm_content":None,#描述信息  
            "cf_flag":0 , # 0:没有，1：有现金流量表 #下边在2015-06-09添加
            "rfm_ngc_gap_revenue":0,
            "rfm_ngc_gap_revenue_inc":0,
            "rfm_ngc_gap_cash":0,
            "rfm_ngc_gap_absolute_cash":0,
            "rfm_main_revenue_evaluated":0,
            "rfm_main_revenue_evmax":0,
            "rfm_main_revenue_evmin1":0,
            "rfm_main_revenue_evmin2":0,
            "rfm_main_cost_evaluated":0,
            "rfm_main_cost_evmax":0,
            "rfm_main_cost_evmin1":0,
            "rfm_main_cost_evmin2":0,
            "rfm_expense_ev":0,
            "rfm_expense_ev_se01":0,
            "rfm_expense_ev_se02":0,
            "rfm_expense_ev_se03":0,  
            "rfm_a1_f2":0, #曹老师方法2估算收入
            "rfm_a2_f2":0, #曹老师方法2估算成本
            "rfm_a3_f2":0, #曹老师方法2估算费用
            "rfm_a1_f3":0,
            "rfm_a2_f3":0,
            "rfm_a3_f3":0,
            "rfm_cash_revu_gap":0, #######2015-06-12添加,为了再整合结果
            "rfm_ngc_real_val":0,
            "rfm_ka_val":0,
            "rfm_ngc_val":0
            }
        ]  
        rfm_main_revenue_evaluated 
    '''
    ent_result={"success":False,"message":""}

    try:
        i_loop =0
        i_count =0
        i_count =len(v_ent)
        for i_loop in range(0,i_count): 
            v=v_ent[i_loop]
            if v["cf_flag"]==0: #没有现金流量表
                _nocash(v)
                pass
            else:   #包含现金流量表的情况
                _hascash(v)
                pass
        ent_result["success"]=True
        pass
    except Exception ,e:
        ent_result["message"]=e
        pass

    return ent_result
    pass 
# 没有现金流量表的处理
def _nocash(v):  
    min_sr=model_get_min2(v["rfm_a1_old"] ,v["rfm_a1"],v["rfm_revenue"],v["rfm_a1_f2"],v["rfm_a1_f3"])
    min_cb=model_get_min2(v["rfm_a2_old"] ,v["rfm_a2"],v["rfm_cost"],v["rfm_a2_f2"])
    min_fy=model_get_min2(v["rfm_a3_old"] ,v["rfm_a3"],v["rfm_exp"],v["rfm_a3_f2"] )



    # print i_loop
    v["rfm_p1"]=abs(abs(min_sr)- abs(float(v["rfm_a1_old"])))
    v["rfm_p2"]=abs(abs(min_cb)- abs(float(v["rfm_a2_old"])))
    v["rfm_p3"]=abs(abs(min_fy)-abs(float(v["rfm_a3_old"])))


    # v["rfm_p1"]=abs(min_sr)- abs(float(v["rfm_a1_old"]))
    # v["rfm_p2"]=abs(min_cb)- abs(float(v["rfm_a2_old"]))
    # v["rfm_p3"]=abs(min_fy)-abs(float(v["rfm_a3_old"]))
    
    # v["rfm_p1"]=min_sr-float(v["rfm_a1_old"])
    # v["rfm_p2"]=min_cb- float(v["rfm_a2_old"])
    # v["rfm_p3"]=min_fy-float(v["rfm_a3_old"])

    if abs(v["rfm_p3"])>=500000:
        if float(v["rfm_a3_old"])!=0 and   abs(v["rfm_p3"]) /abs(float(v["rfm_a3_old"]))>=0.5:
            v["rfm_p3"] = float(v["rfm_a3_old"]) *0.5
    # 把当前估算的做为上限
    # v_temp_p1=v["rfm_p1"]
    # v_temp_p2=v["rfm_p2"]
    # v_temp_p3=v["rfm_p3"]
    if abs(v["rfm_p1"])>=50000000:
        v["rfm_p1"]=v["rfm_p1"]*0.8
        v["rfm_p2"]=v["rfm_p2"]*0.8
        v["rfm_p3"]=v["rfm_p3"]*0.8
    else:
        if abs(v["rfm_p1"])>=20000000:
            v["rfm_p1"]=v["rfm_p1"]*0.85
            v["rfm_p2"]=v["rfm_p2"]*0.85
            v["rfm_p3"]=v["rfm_p3"]*0.85
        else:
            if abs(v["rfm_p1"])>=5000000:
                v["rfm_p1"]=v["rfm_p1"]*0.9
                v["rfm_p2"]=v["rfm_p2"]*0.9
                v["rfm_p3"]=v["rfm_p3"]*0.9


    if abs(v["rfm_p2"])>=50000000:
        v["rfm_p1"]=v["rfm_p1"]*0.8
        v["rfm_p2"]=v["rfm_p2"]*0.8
        v["rfm_p3"]=v["rfm_p3"]*0.8
    else:
        if abs(v["rfm_p2"])>=20000000:
            v["rfm_p1"]=v["rfm_p1"]*0.85
            v["rfm_p2"]=v["rfm_p2"]*0.85
            v["rfm_p3"]=v["rfm_p3"]*0.85
        else:
            if abs(v["rfm_p2"])>=5000000:
                v["rfm_p1"]=v["rfm_p1"]*0.9
                v["rfm_p2"]=v["rfm_p2"]*0.9
                v["rfm_p3"]=v["rfm_p3"]*0.9

    if abs(v["rfm_p3"])>=50000000:
        v["rfm_p1"]=v["rfm_p1"]*0.8
        v["rfm_p2"]=v["rfm_p2"]*0.8
        v["rfm_p3"]=v["rfm_p3"]*0.8
    else:
        if abs(v["rfm_p3"])>=20000000:
            v["rfm_p1"]=v["rfm_p1"]*0.85
            v["rfm_p2"]=v["rfm_p2"]*0.85
            v["rfm_p3"]=v["rfm_p3"]*0.85
        else:
            if abs(v["rfm_p3"])>=5000000:
                v["rfm_p1"]=v["rfm_p1"]*0.9
                v["rfm_p2"]=v["rfm_p2"]*0.9
                v["rfm_p3"]=v["rfm_p3"]*0.9
    # if abs(v_temp_p1-v_temp_p2-v_temp_p3)<abs(float(v["rfm_p1"]) - float(v["rfm_p2"]) -float(v["rfm_p3"])):
        # v["rfm_p1"]=v_temp_p1
        # v["rfm_p2"]=v_temp_p2
        # v["rfm_p3"]=v_temp_p2

    # 利润差额
    ubound=0
    lbound=0 
    v["rfm_profit"]= float(v["rfm_p1"]) - float(v["rfm_p2"]) -float(v["rfm_p3"])   #float(v["rfm_p1"]) -float(v["rfm_a1"])- float(v["rfm_p2"]) +float(v["rfm_a2"]) - float(v["rfm_p3"]) + float(v["rfm_a3"])
    
    v_t_p_pft =abs(abs(float(v["rfm_p1"]))-abs(v["rfm_a2_f3"]-v["rfm_a2_old"]))

    if  abs(v["rfm_profit"])>v_t_p_pft:
        v["rfm_profit"]=v_t_p_pft
    # v["rfm_profit"]= float(v["rfm_p1"]) - float(v["rfm_p2"])
    ################## ''' 先进行利润差额的处理'''
    # print '####################################'
    # 需要特别注意，这里传入的参数一与二是相同的，即为了处理一下，不应用第二个参数
    v_temp_profit=_get_valid4items(v["rfm_ngc_gap_revenue"],v["rfm_ngc_gap_revenue"],v["rfm_ngc_gap_cash"],v["rfm_ngc_gap_absolute_cash"])
    # print 2
    if v_temp_profit !=0:
        if abs(v_temp_profit)<abs(v["rfm_profit"]):
            v["rfm_profit"] =v_temp_profit
    ################## rfm_ngc_gap_revenue ,rfm_ngc_gap_revenue_inc,rfm_ngc_gap_cash,rfm_ngc_gap_absolute_cash
    # 根据情况再次调整 2015-06-12
    # print 3
    rfm_a1_old_temp =model_get_max(abs(v["rfm_a1_old"]),abs(v["rfm_a2_old"]),abs(v["rfm_a3_old"]))
    # print 4
    if rfm_a1_old_temp==0:
        rfm_a1_old_temp=1
    l_temp=0 #用于保存利润差额与得到的收入的比率
    # print 5
    l_temp =  abs(v["rfm_profit"]) /rfm_a1_old_temp 
    # print 5.1
    if l_temp>=0.5 or (abs(v["rfm_profit"])<=1000000 and abs(v["rfm_profit"])>=100000 and v["rfm_ka_val"]<=15):
        try:
            if v["rfm_cash_revu_gap"]!=None and v["rfm_cash_revu_gap"]!=None and v["rfm_ngc_real_val"]!=None:
                # print 5.2
                if abs(v["rfm_cash_revu_gap"])>0 and abs(v["rfm_ngc_real_val"])>0:
                    # print 5.3
                    v["rfm_profit"] =model_get_min(abs(v["rfm_profit"]),abs(v["rfm_cash_revu_gap"]),abs(v["rfm_ngc_real_val"]))
                else:
                    # print 5.4
                    if abs(v["rfm_cash_revu_gap"])>0 :
                        # print 5.5
                        v["rfm_profit"]=model_get_min(abs(v["rfm_profit"]),abs(v["rfm_cash_revu_gap"]))
                    else:
                        # print 5.6
                        v["rfm_profit"]=model_get_min(abs(v["rfm_profit"]),abs(v["rfm_ngc_real_val"]))
        except Exception ,e:
            print e


    l_temp =abs(v["rfm_profit"]/rfm_a1_old_temp)
    # print 6
    if l_temp>=0.5:
        v["rfm_profit"] =rfm_a1_old_temp *0.5 
    if abs(v["rfm_ka_val"])<=10 and v["rfm_ngc_val"]!=None and abs(v["rfm_ngc_val"])<=0.05:
        v["rfm_profit"] =model_get_min(abs(v["rfm_profit"]),abs(v["rfm_ngc_real_val"]))  
    # print 7
    v["rfm_profit"]=abs(v["rfm_profit"])
    if abs(v["rfm_profit"])>1000000:
        bound1=float(v["rfm_profit"])*0.9 
        bound2=float(v["rfm_profit"])*1.1
        pass
    elif abs(v["rfm_profit"])>400000:
        bound1=float(v["rfm_profit"])*0.88 
        bound2=float(v["rfm_profit"])*1.12
        pass
    elif abs(v["rfm_profit"])>50000:
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

    # 收入差额上下限
    ubound=0
    lbound=0
    if abs(v["rfm_p1"])>1000000:
        bound1=float(v["rfm_p1"])*0.9 
        bound2=float(v["rfm_p1"])*1.1
        pass
    elif abs(v["rfm_p1"])>400000:
        bound1=float(v["rfm_p1"])*0.88 
        bound2=float(v["rfm_p1"])*1.12
        pass
    elif abs(v["rfm_p1"])>50000:
        bound1=float(v["rfm_p1"])*0.85 
        bound2=float(v["rfm_p1"])*1.15
        pass
    else:
        bound1=float(v["rfm_p1"])*0.8 
        bound2=float(v["rfm_p1"])*1.2
        pass

    if bound1>bound2:
        ubound=bound1
        lbound=bound2
    else: 
        ubound=bound2
        lbound=bound1
    v["rfm_p1_ubound"]=ubound
    v["rfm_p1_lbound"]=lbound  

    # 成本差额上下限
    ubound=0
    lbound=0
    if abs(v["rfm_p2"])>1000000:
        bound1=float(v["rfm_p2"])*0.9 
        bound2=float(v["rfm_p2"])*1.1
        pass
    elif abs(v["rfm_p2"])>400000:
        bound1=float(v["rfm_p2"])*0.88 
        bound2=float(v["rfm_p2"])*1.12
        pass
    elif abs(v["rfm_p2"])>50000:
        bound1=float(v["rfm_p2"])*0.85 
        bound2=float(v["rfm_p2"])*1.15
        pass
    else:
        bound1=float(v["rfm_p2"])*0.8 
        bound2=float(v["rfm_p2"])*1.2
        pass

    if bound1>bound2:
        ubound=bound1
        lbound=bound2
    else: 
        ubound=bound2
        lbound=bound1
    v["rfm_p2_ubound"]=ubound
    v["rfm_p2_lbound"]=lbound 

    # 费用差额上下限
    ubound=0
    lbound=0
    if abs(v["rfm_p3"])>1000000:
        bound1=float(v["rfm_p3"])*0.9 
        bound2=float(v["rfm_p3"])*1.1
        pass
    elif abs(v["rfm_p3"])>400000:
        bound1=float(v["rfm_p3"])*0.88 
        bound2=float(v["rfm_p3"])*1.12
        pass
    elif abs(v["rfm_p3"])>50000:
        bound1=float(v["rfm_p3"])*0.85 
        bound2=float(v["rfm_p3"])*1.15
        pass
    else:
        bound1=float(v["rfm_p3"])*0.8 
        bound2=float(v["rfm_p3"])*1.2
        pass

    if bound1>bound2:
        ubound=bound1
        lbound=bound2
    else: 
        ubound=bound2
        lbound=bound1
    v["rfm_p3_ubound"]=ubound
    v["rfm_p3_lbound"]=lbound 
    pass

# 有现金流量表的处理
def _hascash(v): 
    min_sr=model_get_min2(v["rfm_a1_old"] ,v["rfm_a1"],v["rfm_revenue"],v["rfm_asien_revenue"],
             v["rfm_main_revenue_evaluated"],v["rfm_main_revenue_evmax"],v["rfm_main_revenue_evmin1"],v["rfm_main_revenue_evmin2"],v["rfm_a1_f2"],v["rfm_a1_f3"])
    min_cb=model_get_min2(v["rfm_a2_old"] ,v["rfm_a2"],v["rfm_cost"],v["rfm_asien_cost"],
             v["rfm_main_cost_evaluated"],v["rfm_main_cost_evmax"],v["rfm_main_cost_evmin1"],v["rfm_main_cost_evmin2"],v["rfm_a2_f2"])
    min_fy=model_get_min2(v["rfm_a3_old"] ,v["rfm_a3"],v["rfm_exp"],v["rfm_asien_exp"],
             v["rfm_expense_ev"],v["rfm_expense_ev_se01"],v["rfm_expense_ev_se02"],v["rfm_expense_ev_se03"],v["rfm_a3_f2"] )
    # print i_loop  
    v["rfm_p1"]=abs(abs(min_sr)- abs(float(v["rfm_a1_old"])))
    v["rfm_p2"]=abs(abs(min_cb)- abs(float(v["rfm_a2_old"])))
    v["rfm_p3"]=abs(abs(min_fy)-abs(float(v["rfm_a3_old"])))


    # v["rfm_p1"]=abs(min_sr)- abs(float(v["rfm_a1_old"]))
    # v["rfm_p2"]=abs(min_cb)- abs(float(v["rfm_a2_old"]))
    # v["rfm_p3"]=abs(min_fy)-abs(float(v["rfm_a3_old"]))
    
    # v["rfm_p1"]=min_sr-float(v["rfm_a1_old"])
    # v["rfm_p2"]=min_cb- float(v["rfm_a2_old"])
    # v["rfm_p3"]=min_fy-float(v["rfm_a3_old"])

    if abs(v["rfm_p3"])>=500000:
        if float(v["rfm_a3_old"])!=0 and   abs(v["rfm_p3"]) /abs(float(v["rfm_a3_old"]))>=0.5:
            v["rfm_p3"] = float(v["rfm_a3_old"]) *0.5
    # 把当前估算的做为上限
    # v_temp_p1=v["rfm_p1"]
    # v_temp_p2=v["rfm_p2"]
    # v_temp_p3=v["rfm_p3"]
    if abs(v["rfm_p1"])>=50000000:
        v["rfm_p1"]=v["rfm_p1"]*0.8
        v["rfm_p2"]=v["rfm_p2"]*0.8
        v["rfm_p3"]=v["rfm_p3"]*0.8
    else:
        if abs(v["rfm_p1"])>=20000000:
            v["rfm_p1"]=v["rfm_p1"]*0.85
            v["rfm_p2"]=v["rfm_p2"]*0.85
            v["rfm_p3"]=v["rfm_p3"]*0.85
        else:
            if abs(v["rfm_p1"])>=5000000:
                v["rfm_p1"]=v["rfm_p1"]*0.9
                v["rfm_p2"]=v["rfm_p2"]*0.9
                v["rfm_p3"]=v["rfm_p3"]*0.9


    if abs(v["rfm_p2"])>=50000000:
        v["rfm_p1"]=v["rfm_p1"]*0.8
        v["rfm_p2"]=v["rfm_p2"]*0.8
        v["rfm_p3"]=v["rfm_p3"]*0.8
    else:
        if abs(v["rfm_p2"])>=20000000:
            v["rfm_p1"]=v["rfm_p1"]*0.85
            v["rfm_p2"]=v["rfm_p2"]*0.85
            v["rfm_p3"]=v["rfm_p3"]*0.85
        else:
            if abs(v["rfm_p2"])>=5000000:
                v["rfm_p1"]=v["rfm_p1"]*0.9
                v["rfm_p2"]=v["rfm_p2"]*0.9
                v["rfm_p3"]=v["rfm_p3"]*0.9

    if abs(v["rfm_p3"])>=50000000:
        v["rfm_p1"]=v["rfm_p1"]*0.8
        v["rfm_p2"]=v["rfm_p2"]*0.8
        v["rfm_p3"]=v["rfm_p3"]*0.8
    else:
        if abs(v["rfm_p3"])>=20000000:
            v["rfm_p1"]=v["rfm_p1"]*0.85
            v["rfm_p2"]=v["rfm_p2"]*0.85
            v["rfm_p3"]=v["rfm_p3"]*0.85
        else:
            if abs(v["rfm_p3"])>=5000000:
                v["rfm_p1"]=v["rfm_p1"]*0.9
                v["rfm_p2"]=v["rfm_p2"]*0.9
                v["rfm_p3"]=v["rfm_p3"]*0.9
    # if abs(v_temp_p1-v_temp_p2-v_temp_p3)<abs(float(v["rfm_p1"]) - float(v["rfm_p2"]) -float(v["rfm_p3"])):
        # v["rfm_p1"]=v_temp_p1
        # v["rfm_p2"]=v_temp_p2
        # v["rfm_p3"]=v_temp_p2

    # 利润差额
    ubound=0
    lbound=0 
    v["rfm_profit"]= float(v["rfm_p1"]) - float(v["rfm_p2"]) -float(v["rfm_p3"])   #float(v["rfm_p1"]) -float(v["rfm_a1"])- float(v["rfm_p2"]) +float(v["rfm_a2"]) - float(v["rfm_p3"]) + float(v["rfm_a3"])
    
    v_t_p_pft =abs(abs(float(v["rfm_p1"]))-abs(v["rfm_a2_f3"]-v["rfm_a2_old"]))

    if  abs(v["rfm_profit"])>v_t_p_pft:
        v["rfm_profit"]=v_t_p_pft
    # v["rfm_profit"]= float(v["rfm_p1"]) - float(v["rfm_p2"])
    ################## ''' 先进行利润差额的处理'''
    # print '####################################'
    # 需要特别注意，这里传入的参数一与二是相同的，即为了处理一下，不应用第二个参数
    v_temp_profit=_get_valid4items(v["rfm_ngc_gap_revenue"],v["rfm_ngc_gap_revenue_inc"],v["rfm_ngc_gap_cash"],v["rfm_ngc_gap_absolute_cash"])
    # print 2
    if v_temp_profit !=0:
        if abs(v_temp_profit)<abs(v["rfm_profit"]):
            v["rfm_profit"] =v_temp_profit
    ################## rfm_ngc_gap_revenue ,rfm_ngc_gap_revenue_inc,rfm_ngc_gap_cash,rfm_ngc_gap_absolute_cash
    # 根据情况再次调整 2015-06-12
    # print 3
    rfm_a1_old_temp =model_get_max(abs(v["rfm_a1_old"]),abs(v["rfm_a2_old"]),abs(v["rfm_a3_old"]))
    # print 4
    if rfm_a1_old_temp==0:
        rfm_a1_old_temp=1
    l_temp=0 #用于保存利润差额与得到的收入的比率
    # print 5
    l_temp =  abs(v["rfm_profit"]) /rfm_a1_old_temp 
    # print 5.1
    if l_temp>=0.5 or (abs(v["rfm_profit"])<=1000000 and abs(v["rfm_profit"])>=100000 and v["rfm_ka_val"]<=15 and v["rfm_ka_val"]>0):
        try:
            if v["rfm_cash_revu_gap"]!=None and v["rfm_cash_revu_gap"]!=None and v["rfm_ngc_real_val"]!=None:
                # print 5.2
                if abs(v["rfm_cash_revu_gap"])>0 and abs(v["rfm_ngc_real_val"])>0:
                    # print 5.3
                    v["rfm_profit"] =model_get_min(abs(v["rfm_profit"]),abs(v["rfm_cash_revu_gap"]),abs(v["rfm_ngc_real_val"]))
                else:
                    # print 5.4
                    if abs(v["rfm_cash_revu_gap"])>0 :
                        # print 5.5
                        v["rfm_profit"]=model_get_min(abs(v["rfm_profit"]),abs(v["rfm_cash_revu_gap"]))
                    else:
                        # print 5.6
                        v["rfm_profit"]=model_get_min(abs(v["rfm_profit"]),abs(v["rfm_ngc_real_val"]))
        except Exception ,e:
            print e


    l_temp =abs(v["rfm_profit"]/rfm_a1_old_temp)
    # print 6
    if l_temp>=0.5:
        v["rfm_profit"] =rfm_a1_old_temp *0.5 
    if abs(v["rfm_ka_val"])<=10 and v["rfm_ngc_val"]!=None and abs(v["rfm_ngc_val"])<=0.05:
        v["rfm_profit"] =model_get_min(abs(v["rfm_profit"]),abs(v["rfm_ngc_real_val"]))  
    # print 7
    v["rfm_profit"]=abs(v["rfm_profit"])
    if abs(v["rfm_profit"])>1000000:
        bound1=float(v["rfm_profit"])*0.9 
        bound2=float(v["rfm_profit"])*1.1
        pass
    elif abs(v["rfm_profit"])>400000:
        bound1=float(v["rfm_profit"])*0.88 
        bound2=float(v["rfm_profit"])*1.12
        pass
    elif abs(v["rfm_profit"])>50000:
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

    # 收入差额上下限
    ubound=0
    lbound=0
    if abs(v["rfm_p1"])>1000000:
        bound1=float(v["rfm_p1"])*0.9 
        bound2=float(v["rfm_p1"])*1.1
        pass
    elif abs(v["rfm_p1"])>400000:
        bound1=float(v["rfm_p1"])*0.88 
        bound2=float(v["rfm_p1"])*1.12
        pass
    elif abs(v["rfm_p1"])>50000:
        bound1=float(v["rfm_p1"])*0.85 
        bound2=float(v["rfm_p1"])*1.15
        pass
    else:
        bound1=float(v["rfm_p1"])*0.8 
        bound2=float(v["rfm_p1"])*1.2
        pass

    if bound1>bound2:
        ubound=bound1
        lbound=bound2
    else: 
        ubound=bound2
        lbound=bound1
    v["rfm_p1_ubound"]=ubound
    v["rfm_p1_lbound"]=lbound  

    # 成本差额上下限
    ubound=0
    lbound=0
    if abs(v["rfm_p2"])>1000000:
        bound1=float(v["rfm_p2"])*0.9 
        bound2=float(v["rfm_p2"])*1.1
        pass
    elif abs(v["rfm_p2"])>400000:
        bound1=float(v["rfm_p2"])*0.88 
        bound2=float(v["rfm_p2"])*1.12
        pass
    elif abs(v["rfm_p2"])>50000:
        bound1=float(v["rfm_p2"])*0.85 
        bound2=float(v["rfm_p2"])*1.15
        pass
    else:
        bound1=float(v["rfm_p2"])*0.8 
        bound2=float(v["rfm_p2"])*1.2
        pass

    if bound1>bound2:
        ubound=bound1
        lbound=bound2
    else: 
        ubound=bound2
        lbound=bound1
    v["rfm_p2_ubound"]=ubound
    v["rfm_p2_lbound"]=lbound 

    # 费用差额上下限
    ubound=0
    lbound=0
    if abs(v["rfm_p3"])>1000000:
        bound1=float(v["rfm_p3"])*0.9 
        bound2=float(v["rfm_p3"])*1.1
        pass
    elif abs(v["rfm_p3"])>400000:
        bound1=float(v["rfm_p3"])*0.88 
        bound2=float(v["rfm_p3"])*1.12
        pass
    elif abs(v["rfm_p3"])>50000:
        bound1=float(v["rfm_p3"])*0.85 
        bound2=float(v["rfm_p3"])*1.15
        pass
    else:
        bound1=float(v["rfm_p3"])*0.8 
        bound2=float(v["rfm_p3"])*1.2
        pass

    if bound1>bound2:
        ubound=bound1
        lbound=bound2
    else: 
        ubound=bound2
        lbound=bound1
    v["rfm_p3_ubound"]=ubound
    v["rfm_p3_lbound"]=lbound 
    pass
# 有现金流量表的处理
# def _hascash(v): 
#     min_sr=model_get_min2(v["rfm_a1_old"] ,v["rfm_a1"],v["rfm_revenue"],v["rfm_asien_revenue"],
#              v["rfm_main_revenue_evaluated"],v["rfm_main_revenue_evmax"],v["rfm_main_revenue_evmin1"],v["rfm_main_revenue_evmin2"],v["rfm_a1_f2"],v["rfm_a1_f3"])
#     min_cb=model_get_min2(v["rfm_a2_old"] ,v["rfm_a2"],v["rfm_cost"],v["rfm_asien_cost"],
#              v["rfm_main_cost_evaluated"],v["rfm_main_cost_evmax"],v["rfm_main_cost_evmin1"],v["rfm_main_cost_evmin2"],v["rfm_a2_f2"])
#     min_fy=model_get_min2(v["rfm_a3_old"] ,v["rfm_a3"],v["rfm_exp"],v["rfm_asien_exp"],
#              v["rfm_expense_ev"],v["rfm_expense_ev_se01"],v["rfm_expense_ev_se02"],v["rfm_expense_ev_se03"],v["rfm_a3_f2"] )
#     # print i_loop
#     v["rfm_p1"]=abs(abs(min_sr)-abs(float(v["rfm_a1_old"])))
#     v["rfm_p2"]=abs(abs(min_cb)-abs(float(v["rfm_a2_old"])))
#     v["rfm_p3"]=abs(abs(min_fy)-abs(float(v["rfm_a3_old"])))

#     if abs(v["rfm_p3"])>=500000:
#         if float(v["rfm_a3_old"])!=0 and   abs(v["rfm_p3"] /float(v["rfm_a3_old"]))>=0.5:
#             v["rfm_p3"] = float(v["rfm_a3_old"]) *0.5
#     # 利润差额
#     ubound=0
#     lbound=0
#     v["rfm_profit"]= float(v["rfm_p1"]) - float(v["rfm_p2"]) -float(v["rfm_p3"])   #float(v["rfm_p1"]) -float(v["rfm_a1"])- float(v["rfm_p2"]) +float(v["rfm_a2"]) - float(v["rfm_p3"]) + float(v["rfm_a3"])
#     ################## ''' 先进行利润差额的处理'''
#     v_temp_profit=_get_valid4items(v["rfm_ngc_gap_revenue"],v["rfm_ngc_gap_revenue_inc"],v["rfm_ngc_gap_cash"],v["rfm_ngc_gap_absolute_cash"])
    
#     if v_temp_profit !=0:
#         if abs(v_temp_profit)<abs(v["rfm_profit"]):
#             v["rfm_profit"] =v_temp_profit
#     ################## rfm_ngc_gap_revenue ,rfm_ngc_gap_revenue_inc,rfm_ngc_gap_cash,rfm_ngc_gap_absolute_cash


#  # 根据情况再次调整 2015-06-12
#     rfm_a1_old_temp =model_get_max(abs(v["rfm_a1_old"]),abs(v["rfm_a2_old"]),abs(v["rfm_a3_old"]))
#     rfm_a1_old_temp =abs(v["rfm_p1"]+v["rfm_a1_old"])
#     if rfm_a1_old_temp==0:
#         rfm_a1_old_temp=1
#     l_temp=0 #用于保存利润差额与得到的收入的比率

#     l_temp =  abs(v["rfm_profit"]) /rfm_a1_old_temp 
#     if l_temp>=0.5 or (abs(v["rfm_profit"])<=1000000 and abs(v["rfm_profit"])>=100000 and v["rfm_ka_val"]<=15):
#         if abs(v["rfm_cash_revu_gap"])>0 and abs(v["rfm_ngc_real_val"])>0:
#             v["rfm_profit"] =model_get_min(abs(v["rfm_profit"]),abs(v["rfm_cash_revu_gap"]),abs(v["rfm_ngc_real_val"]))
#         else:
#             if abs(v["rfm_cash_revu_gap"])>0 :
#                 v["rfm_profit"]=model_get_min(abs(v["rfm_profit"]),abs(v["rfm_cash_revu_gap"]))
#             else:
#                 v["rfm_profit"]=model_get_min(abs(v["rfm_profit"]),abs(v["rfm_ngc_real_val"]))

#     l_temp =abs(v["rfm_profit"]/rfm_a1_old_temp)

#     if l_temp>=0.5:
#         v["rfm_profit"] =rfm_a1_old_temp *0.5 
#     if abs(v["rfm_ka_val"])<=10 and abs(v["rfm_ngc_val"])<=0.05:
#         v["rfm_profit"] =model_get_min(abs(v["rfm_profit"]),abs(v["rfm_ngc_real_val"]))  
#     if abs(v["rfm_profit"])>1000000:
#         bound1=float(v["rfm_profit"])*0.9 
#         bound2=float(v["rfm_profit"])*1.1
#         pass
#     elif abs(v["rfm_profit"])>400000:
#         bound1=float(v["rfm_profit"])*0.88 
#         bound2=float(v["rfm_profit"])*1.12
#         pass
#     elif abs(v["rfm_profit"])>50000:
#         bound1=float(v["rfm_profit"])*0.85 
#         bound2=float(v["rfm_profit"])*1.15
#         pass
#     else:
#         bound1=float(v["rfm_profit"])*0.8 
#         bound2=float(v["rfm_profit"])*1.2
#         pass

#     if bound1>bound2:
#         ubound=bound1
#         lbound=bound2
#     else: 
#         ubound=bound2
#         lbound=bound1
#     v["rfm_profit_ubound"]=ubound
#     v["rfm_profit_lbound"]=lbound  

#     # 收入差额上下限
#     ubound=0
#     lbound=0
#     if abs(v["rfm_p1"])>1000000:
#         bound1=float(v["rfm_p1"])*0.9 
#         bound2=float(v["rfm_p1"])*1.1
#         pass
#     elif abs(v["rfm_p1"])>400000:
#         bound1=float(v["rfm_p1"])*0.88 
#         bound2=float(v["rfm_p1"])*1.12
#         pass
#     elif abs(v["rfm_p1"])>50000:
#         bound1=float(v["rfm_p1"])*0.85 
#         bound2=float(v["rfm_p1"])*1.15
#         pass
#     else:
#         bound1=float(v["rfm_p1"])*0.8 
#         bound2=float(v["rfm_p1"])*1.2
#         pass

#     if bound1>bound2:
#         ubound=bound1
#         lbound=bound2
#     else: 
#         ubound=bound2
#         lbound=bound1
#     v["rfm_p1_ubound"]=ubound
#     v["rfm_p1_lbound"]=lbound  

#     # 成本差额上下限
#     ubound=0
#     lbound=0
#     if abs(v["rfm_p2"])>1000000:
#         bound1=float(v["rfm_p2"])*0.9 
#         bound2=float(v["rfm_p2"])*1.1
#         pass
#     elif abs(v["rfm_p2"])>400000:
#         bound1=float(v["rfm_p2"])*0.88 
#         bound2=float(v["rfm_p2"])*1.12
#         pass
#     elif abs(v["rfm_p2"])>50000:
#         bound1=float(v["rfm_p2"])*0.85 
#         bound2=float(v["rfm_p2"])*1.15
#         pass
#     else:
#         bound1=float(v["rfm_p2"])*0.8 
#         bound2=float(v["rfm_p2"])*1.2
#         pass

#     if bound1>bound2:
#         ubound=bound1
#         lbound=bound2
#     else: 
#         ubound=bound2
#         lbound=bound1
#     v["rfm_p2_ubound"]=ubound
#     v["rfm_p2_lbound"]=lbound 

#     # 费用差额上下限
#     ubound=0
#     lbound=0
#     if abs(v["rfm_p3"])>1000000:
#         bound1=float(v["rfm_p3"])*0.9 
#         bound2=float(v["rfm_p3"])*1.1
#         pass
#     elif abs(v["rfm_p3"])>400000:
#         bound1=float(v["rfm_p3"])*0.88 
#         bound2=float(v["rfm_p3"])*1.12
#         pass
#     elif abs(v["rfm_p3"])>50000:
#         bound1=float(v["rfm_p3"])*0.85 
#         bound2=float(v["rfm_p3"])*1.15
#         pass
#     else:
#         bound1=float(v["rfm_p3"])*0.8 
#         bound2=float(v["rfm_p3"])*1.2
#         pass

#     if bound1>bound2:
#         ubound=bound1
#         lbound=bound2
#     else: 
#         ubound=bound2
#         lbound=bound1
#     v["rfm_p3_ubound"]=ubound
#     v["rfm_p3_lbound"]=lbound 
#     pass
# rfm_ngc_gap_revenue ,rfm_ngc_gap_revenue_inc,rfm_ngc_gap_cash,rfm_ngc_gap_absolute_cash
def _get_valid4items(v1,v2,v3,v4):
    param1=v1
    param2=v2
    param3=v3
    param4=v4
    if param2<0:
        param2=0
    else:
        param2=param2

    v_return=0
    if param1==None:
        param1=0
    if param2==None:
        param2 =0
    if param3==None:
        param3 =0
    if param4==None:
        param4 =0

    v_temp=(param1,param2,param3,param4)
    for v in v_temp:
        if v!=0:
            if v_return==0:
                v_return =v
            else:
                if abs(v)<abs(v_return):
                    v_return=v
    return v_return
    pass
def tttt():  
    v_ent=[
        {
            "firm_code":'test', #企业代码
            "por":'2015-01-31', #所属期
            "dt_property":21, #数据属性标志
            "dt_type":1, #数据类型
            "dt_source":None, #数据来源
            "order_id":'111111111111111111111', #订单号
            "rfm_a1_old":100, #申报收入
            "rfm_a2_old":200, #申报成本
            "rfm_a3_old":300, #申报费用
            "rfm_a1":1, #曹老师估算收入
            "rfm_a2":2, #曹老师估算成本
            "rfm_a3":3, #曹老师估算费用
            "rfm_revenue":4, #吴老师估算收入
            "rfm_cost":5, #吴老师估算成本
            "rfm_exp":66, #吴老师估算费用
            "rfm_asien_revenue":12, #陈博士估算收入
            "rfm_asien_cost":12, #陈博士估算成本
            "rfm_asien_exp":12, #陈博士估算费用
            "rfm_p1":None, #整理后的收入
            "rfm_p2":None, #整理后的成本
            "rfm_p3":None, #整理后的费用
            "rfm_profit":None, #利润差额
            "rfm_profit_ubound":None, #利润差额上限
            "rfm_profit_lbound":None, #利润差额下限
            "rfm_content":None,#描述信息 
            "cf_flag":0 , # 0:没有，1：有现金流量表 #下边在2015-06-09添加
            "rfm_ngc_gap_revenue":80,
            "rfm_ngc_gap_revenue_inc":0,
            "rfm_ngc_gap_cash":100,
            "rfm_ngc_gap_absolute_cash":0,
            "rfm_main_revenue_evaluated":0,
            "rfm_main_revenue_evmax":0,
            "rfm_main_revenue_evmin1":0,
            "rfm_main_revenue_evmin2":0,
            "rfm_main_cost_evaluated":0,
            "rfm_main_cost_evmax":190,
            "rfm_main_cost_evmin1":0,
            "rfm_main_cost_evmin2":0,
            "rfm_expense_ev":0,
            "rfm_expense_ev_se01":0,
            "rfm_expense_ev_se02":0,
            "rfm_expense_ev_se03":0,  
            "rfm_a1_f2":1, #曹老师方法2估算收入
            "rfm_a2_f2":1, #曹老师方法2估算成本
            "rfm_a3_f2":1, #曹老师方法2估算费用
            }
        ] 
    v_ent=[{
            'rfm_p1_lbound': 0,
            'por':" datetime.datetime(2007,3,31,0,0)",
            'rfm_main_cost_evmax': 192766450.0,
            'rfm_a2_f2': 197612879.6163,
            'rfm_p2_ubound': 0,
            'rfm_asien_cost': 258305000.0,
            'rfm_p3_ubound': 0,
            'rfm_main_cost_evaluated': 258305000.0,
            'rfm_content': None,
            'pa22030_fin_exp': 21057700.0,
            'rfm_profit': 0,
            'dt_property': 1,
            'dt_type': '1',
            'rfm_p2_lbound': 0,
            'pa100t_op_revenue': 203633000.0,
            'pa200t_op_cost': 201484000.0,
            'cf_flag': 1,
            'rfm_asien_exp': -57349060.0,
            'rfm_a1_f2': 209375632.3288,
            'rfm_a1_old': 203633000.0,
            'rfm_cost': '158360011.82995957',
            'rfm_p2': 0,
            'rfm_p3': 0,
            'rfm_ngc_gap_absolute_cash': -203088000.0,
            'rfm_p1': 0,
            'rfm_a3_f2': 59196301.4837,
            'rfm_expense_ev_se02': -57349060.0,
            'rfm_expense_ev_se03': 56080940.0,
            'rfm_p1_ubound': 0,
            'rfm_expense_ev_se01': -57349060.0,
            'rfm_profit_ubound': 0,
            'rfm_revenue': '188556608.30118123',
            'rfm_ngc_gap_revenue_inc': 0.0,
            'rfm_main_cost_evmin1': 273119000.0,
            'rfm_main_cost_evmin2': 144875000.0,
            'rfm_expense_ev': 56080940.0,
            'rfm_ngc_gap_cash': -203088000.0,
            'rfm_a2_old': 201484000.0,
            'rfm_profit_lbound': 0,
            'rfm_main_revenue_evmin2': 158256850.0,
            'rfm_main_revenue_evmin1': 161934450.0,
            'rfm_a3_old': 42579150.0,
            'rfm_asien_revenue': 158256850.0,
            'rfm_exp': '77719565.84376892',
            'pa22010_sales_exp': 7804650.0,
            'rfm_ngc_gap_revenue': 712239300.0,
            'dt_source': None,
            'pa22020_admin_exp': 13716800.0,
            'firm_code': '600895',
            'rfm_p3_lbound': 0,
            'rfm_main_revenue_evaluated':0, 
            'rfm_main_revenue_evmax':0,
            'rfm_a1': 228306457.7833,
            'rfm_a3': 70605431.7434,
            'rfm_a2': 180090546.7152, 
            "rfm_cash_revu_gap":110, #######2015-06-12添加,为了再整合结果
            "rfm_ngc_real_val":10,
            "rfm_ka_val":0,
            "rfm_ngc_val":0
        }]
    v_ent=[{
        'rfm_p1_lbound': 9205966.828097964,
        'por': '2015-01-31',
        'rfm_main_cost_evmax': 322507800.0,
        'rfm_a2_f2': 880348098.8210871,
        'rfm_p2_ubound': 110555608.70319584,
        'rfm_asien_cost': 324658900.0,
        'rfm_main_revenue_evmax': 424007250.0,
        'rfm_p3_ubound': -5451894.70725351,
        'rfm_main_cost_evaluated': 324658900.0,
        'rfm_content': None,
        'rfm_profit': 0,
        'dt_property': 21,
        'dt_type': 1,
        'rfm_p2_lbound': 90454588.93897842,
        'rfm_ka_val': 7.116331096196868,
        'rfm_exp': -193764160.97635636,
        'cf_flag': 1,
        'rfm_asien_exp': 124683665.0,
        'rfm_a1_f2': 622073187.8973604,
        'rfm_a1_old': 594571000.0,
        'rfm_cost': 615554548.660323,
        'rfm_p2': 100505098.82108712,
        'rfm_p3': -6057660.785837233,
        'rfm_ngc_gap_absolute_cash': 0,
        'rfm_p1': 10228852.03121996,
        'rfm_a3_f2': 124584324.07745749,
        'rfm_asien_revenue': 432105600.0,
        'rfm_expense_ev_se03': 186612665.0,
        'rfm_p1_ubound': 11251737.234341957,
        'rfm_expense_ev_se01': 124683665.0,
        'rfm_profit_ubound': 0.0,
        'rfm_revenue': 604799852.03122,
        'rfm_ngc_gap_revenue_inc': 0.0,
        'rfm_ngc_real_val': 0,
        'rfm_main_cost_evmin1': 260578800.0,
        'rfm_main_cost_evmin2': 262729900.0,
        'rfm_expense_ev': 186612665.0,
        'rfm_cash_revu_gap': 181384000.0,
        'rfm_ngc_gap_cash': 0,
        'rfm_a2_old': 779843000.0,
        'rfm_profit_lbound': 0.0,
        'rfm_main_revenue_evmin2': 432105600.0,
        'rfm_main_revenue_evmin1': 409908500.0,
        'rfm_a3_old': 157631500.0,
        'rfm_expense_ev_se02': 124683665.0,
        'rfm_main_revenue_evaluated': 446204350.0,
        'rfm_ngc_val': 0.10,
        'rfm_profit_old': -342903500.0,
        'order_id': '111111111111111111111',
        'rfm_ngc_gap_revenue': 987976190.0,
        'dt_source': None,
        'firm_code': 'test',
        'rfm_p3_lbound': -6663426.864420957,
        'rfm_a1': 695993057.8339405,
        'rfm_a3': 151573839.21416277,
        'rfm_a2': 980552495.6948085
    }]

    v_ent=[{
        'rfm_p1_lbound':0,
        'por':0,
        'rfm_main_cost_evmax':-840969905.37,
        'rfm_a2_f2':1801858598.963,
        'rfm_p2_ubound':0,
        'rfm_asien_cost':336467419.98,
        'rfm_main_revenue_evmax':2204874037.6,
        'rfm_p3_ubound':0,
        'rfm_main_cost_evaluated':336467419.98,
        'rfm_content':0,
        'rfm_profit':0,
        'dt_property':0,
        'dt_type':0,
        'rfm_p2_lbound':0,
        'rfm_ka_val':25.092,
        'rfm_exp':154990661.812,
        'cf_flag':1,
        'rfm_asien_exp':-195101404.3,
        'rfm_a1_f2':342334816.24,
        'rfm_a1_old':928082859.18,
        'rfm_cost':869314358.774,
        'rfm_p2':0,
        'rfm_p3':0,
        'rfm_ngc_gap_absolute_cash':-941148723.03,
        'rfm_p1':0,
        'rfm_a3_f2':6084610.94,
        'rfm_asien_revenue':728721039.18,
        'rfm_expense_ev_se03':45100075.69,
        'rfm_p1_ubound':0,
        'rfm_expense_ev_se01':-195101404.3,
        'rfm_profit_ubound':0,
        'rfm_revenue':516727555.626,
        'rfm_ngc_gap_revenue_inc':3222231124.95,
        'rfm_ngc_real_val':-138325116.07,
        'rfm_main_cost_evmin1':-1081171385.36,
        'rfm_main_cost_evmin2':96265939.99,
        'rfm_expense_ev':45100075.69,
        'rfm_cash_revu_gap':-138325116.07,
        'rfm_ngc_gap_cash':319583818.6,
        'rfm_a2_old':957777795.38,
        'rfm_profit_lbound':0,
        'rfm_main_revenue_evmin2':728721039.18,
        'rfm_main_revenue_evmin1':2054924331.92,
        'rfm_a3_old':700570695.13,
        'rfm_expense_ev_se02':-195101404.3,
        'rfm_main_revenue_evaluated':878670744.86,
        'rfm_ngc_val':-0.007,
        'rfm_profit_old':-730265631.33,
        'order_id':0,
        'rfm_ngc_gap_revenue':0,
        'dt_source':0,
        'firm_code':0,
        'rfm_p3_lbound':0,
        'rfm_a1':0,
        'rfm_a3':0,
        'rfm_a2':0
    }]

    v_rst =rst_generic2(v_ent)
    for v in  v_ent:
        print v['rfm_profit'],v['rfm_profit_ubound'],v['rfm_profit_lbound'] 
        print v['rfm_p1'],v['rfm_p1_ubound'],v['rfm_p1_lbound']
        print v['rfm_p2'],v['rfm_p2_ubound'],v['rfm_p2_lbound']
        print v['rfm_p3'],v['rfm_p3_ubound'],v['rfm_p3_lbound']
    pass
    # print v_rst["message"] ,v_rst["success"]


# tttt()  

