# -*- coding:utf-8 -*-
'''
    交易流水单，读取操作
    创建日期：2015-07-13
'''
import xlrd
def tranflow_reader(v_file):
    '''
        交易流水单操作主方法，
        v_file:文件名
    '''
    obj_return={"success":False,"message":"","data":""}
    file_ext_arr = v_file.split('.')
    file_ext=""
    bln_flag =False
    if len(file_ext_arr)>=2:
        file_ext=file_ext_arr[len(file_ext_arr)-1]
        bln_flag=True
    if bln_flag==False:
        obj_return["message"]="无法判断文件类型"
    else:
        if file_ext.lower()=="txt":
            return _read_txt(v_file)
            pass
        elif file_ext.lower()=="xls":
            return _read_xls(v_file)
            pass
        elif file_ext.lower()=="xlsx":
            return _read_xls(v_file)
            pass
        else:
            obj_return["message"]="不是常见的文件格式"
        pass
    return obj_return
    pass

def _read_txt(v_file):
    obj_return={"success":False,"message":"","data":""}
    fileHandler=None
    i_loop=0
    i_count=0
    try: 
        fileHandler=open(v_file,"r")
        file_lines =fileHandler.readlines() 
        i_count =len(file_lines)
        i_loop =0
        arr_data=[]
        for i_loop in range(1,i_count):
            line_obj = file_lines[i_loop]
            if line_obj.strip()=="":
                continue
            line_cell =line_obj.split(",") 
            if len(line_cell)<3:
                continue
            arr_data.append("%s,%s\n" % (line_cell[0].replace("\r",'').replace("\n",''),line_cell[2].replace("\r",'').replace("\n",'')))
            

        obj_return["data"]="".join(arr_data)
        obj_return["success"]=True
        pass
    except Exception ,e:
        obj_return["message"]= "%s \r\n Error in line:%s" %(e,i_loop)
    finally:
        if fileHandler!=None:
            fileHandler.close()

    return obj_return
    pass
def _read_xls(v_file):
    obj_return={"success":False,"message":"","data":""}

    i_loop=0
    i_count=0
    arr_data=[]
    try:
        obj_read=xlrd.open_workbook(v_file)
        arr =obj_read.sheets()
        for v_sheet in arr: 
            iRowCount =v_sheet.nrows
            iColCount =v_sheet.ncols 

            if iColCount<3:
                continue
            for i_loop in range(1,iRowCount):
                arr_data.append("%s,%s\n" % (v_sheet.cell(i_loop,0).value,v_sheet.cell(i_loop,2).value))
                

        obj_return["data"]="".join(arr_data)
        obj_return["success"]=True
        pass
    except Exception ,e:
        obj_return["message"]= e
    finally:
        pass
    return obj_return
    pass
def _read_xlsx(v_file):
    obj_return={"success":False,"message":"","data":""}
    try:

        obj_return["success"]=True
        pass
    except Exception ,e:
        obj_return["message"]=e
    return obj_return

    pass

def _generic_data(v):
    pass