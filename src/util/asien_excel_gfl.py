# -*- coding: utf-8 -*-

class AsienExcelGFL: 
    def _analyze_report_name(self,v,entities):

        bln_return=False
        temp_str =v
        for ent in entities:
            test_str =ent['caption']
            if test_str in temp_str:
                if ent['type']=='and': 
                    bln_return=True
                    # ent['checked']=True
                elif ent['type']=='not':
                    bln_return=False
                    break
            else:
                if ent['type']=='and': 
                    # ent['checked']=False
                    bln_return=False
                    break
                elif ent['type']=='not':
                    # ent['checked']=True
                    bln_return=True  
        return bln_return
    #判断当前sheet的报表类型 返回为 BS,PL,CF,VAT
    def _check_report_name(self,arr):
        str_report_name=''

        entities={
        'BS':[
            {
                'caption':'固定资产',
                'type':'and'
            },
            {
                'caption':'负债合计',
                'type':'and'
            },
            {
                'caption':'流动负债',
                'type':'and' 
            },
            {
                'caption':'税率',
                'type':'not'
            }],
        'PL':[
            {
                'caption':'净利润',
                'type':'and'
            },
            {
                'caption':'财务费用',
                'type':'and'
            },
            {
                'caption':'税率',
                'type':'not'
            }],
        'CF':[
            {
                'caption':'现金流入',
                'type':'and'
            },
            {
                'caption':'现金流出',
                'type':'and'
            }],
        'VAT':[
            {
                'caption':'一般货物、劳务和应税服务',
                'type':'and'
            },
            {
                'caption':'应税货物销售额',
                'type':'and'
            },
            {
                'caption':'即征即退货物、劳务和应税服务',
                'type':'and' 
            } ],
        'ICT':[
            {
                'caption':'利润总额',
                'type':'and'
            },
            {
                'caption':'财务费用',
                'type':'and'
            },
            {
                'caption':'税率',
                'type':'and' 
            }] 
        }

        bln_flag=False
        arr_temp=[]
        for v in arr:
            arr_temp.append(','.join(v))

        str_temp =','.join(arr_temp) 
        str_report_name=''
        for key,value in entities.items():
            if self._analyze_report_name(str_temp,value):
                str_report_name=key
                break;

        return str_report_name
        