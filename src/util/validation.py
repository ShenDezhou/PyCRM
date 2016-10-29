# -*-coding:utf-8-*-
__author__ = "GILANG (wangjinlong@asiencredit.com)"

import re
import datetime
import random
import time


#定义验证身份证号
def is_valid_idcard(ic_serial):
    #权重数组
    iW = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2, 1];
    #身份证号码中可能的字符
    values = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'x']
    #使用正则表达式检测
    icre = re.compile('^[1-9][0-9]{16}[x0-9]$', re.IGNORECASE);
    m = icre.match(ic_serial);
    if m:
        pass;
    else:
        #不是合法的身份证号码，直接退出
        return False;
    S = 0;
    for i in range(0,17):
        S += int(ic_serial[i]) * iW[i];
    chk_val = (12 - (S % 11)) % 11;
    return ic_serial[17].lower() == values[chk_val];

def is_valid_number(num):
    try:
        float(num)
        return True
    except:
        return False

#验证邮箱
def is_valid_email(email):
    pattern = re.compile(r'^(\w)+(\.\w+)*@(\w)+((\.\w+)+)$')
    match = pattern.match(email)
    if not match:
        return False
    return True


#验证手机号码
def is_valid_tel(phone):
    pattern = re.compile(r'^(0[0-9]{2,3}\-)?([2-9][0-9]{6,7})+(\-[0-9]{1,4})?$')
    match = pattern.match(phone)
    if not match:
        return False
    return True


def is_valid_phone(tel):
    """
    验证电话
    :param tel:
    :return:
    """
    pattern = re.compile(r'(^[0-9]{3,4}\-[0-9]{7,8}$)|(^[0-9]{7,8}$)|(^\([0-9]{3,4}\)[0-9]{3,8}$)|(^1\d{10}$)|(^[0-9\-]{6,30}$)')
    match = pattern.match(tel)
    if not match:
        return False
    return True


def is_valid_password(password):
    """
    检测密码
    :param password:
    :return:
    """
    pattern = re.compile(r'^[\@A-Za-z0-9\!\#\$\%\^\&\*\.\~]{6,22}$')
    match = pattern.match(password)
    if not match:
        return False
    return True


def is_valid_date(str):
    '''
    判断是否是一个有效的日期字符串
    :param str:
    '''
    try:
        print str
        date = str.split('-')
        y = int(date[0])
        m = int(date[1])
        d = int(date[2])
        print y
        print m
        print d
        datetime.date(y,m,d)
        return True
    except:
        return False


#获取一个随即递增的字符串
def randomStr():
    """
        create a random increasing string serial
        create by gilang
    """
    rand = '%s'% int(time.time()) + '%s' % random.randint(0, 99999999999)
    #print rand
    return rand


#判断用户名是否合法
def is_valid_name(name):
    if re.match("^[a-z0-9_]+$", name) and 6 <= len(name) <= 22:
        return True
    return False


#判断用户名是否合法
def is_slave_valid_name(name):
    if re.match("^[a-zA-Z0-9_#]+$", name) and 6 <= len(name) <= 12:
        return True
    return False

#半段价格是否合法
def is_valid_price(price):
    #if re.match("\\d+(\\.\\d+)?(人民币|RMB|￥|美元|\\$)", price):
    if re.match("\\d+(\\.\\d{1,2})", price):
        return True
    return False


#是否是图片
def is_valid_picture(picobj, extlist = ['png', 'jpg', 'gif']):

    tp = filetype(picobj)
    if tp in extlist:
        return True
    return False


import struct
# 支持文件类型
# 用16进制字符串的目的是可以知道文件头是多少字节
# 各种文件头的长度不一样，少半2字符，长则8字符
def typeList():
    return {
            "52617221": "EXT_RAR",
            "504B0304": "EXT_ZIP",
            "FFD8FF": "EXT_JPEG",
            "89504E47": "EXT_PNG",
            "47494638": "EXT_GIF",
            "49492A00": "EXT_TIFF",
            "424D": "EXT_BMP",
            "41433130": "EXT_DWG",
            "38425053": "EXT_PSD",
            "7B5C727466": "EXT_RTF",
            "3C3F786D6C": "EXT_XML",
            "68746D6C3E": "EXT_HTML",
            "44656C69766572792D646174653A": "EXT_EML",
            "CFAD12FEC5FD746F": "EXT_DBX",
            "2142444E": "EXT_PST",
            "000001BA": "EXT_MPG",
            "000001B3": "EXT_MPG",
            "2E524D46": "EXT_RM",
            "57415645": "EXT_WAV",
            "41564920": "EXT_AVI",
            "6D6F6F76": "EXT_MOV",
            "3026B2758E66CF11": "EXT_ASF",
            "4D546864": "EXT_MID",
            "255044462D312E": "EXT_PDF"}
"""
文件格式    文件头(十六进制)
JPEG (jpg)    FFD8FF
PNG (png)    89504E47
GIF (gif)    47494638
TIFF (tif)    49492A00
Windows Bitmap (bmp)    424D
CAD (dwg)    41433130
Adobe Photoshop (psd)    38425053
Rich Text Format (rtf)    7B5C727466
XML (xml)    3C3F786D6C
HTML (html)    68746D6C3E
Email [thorough only] (eml)    44656C69766572792D646174653A
Outlook Express (dbx)    CFAD12FEC5FD746F
Outlook (pst)    2142444E
MS Word/Excel (xls.or.doc)    D0CF11E0
MS Access (mdb)    5374616E64617264204A
WordPerfect (wpd)    FF575043
Postscript (eps.or.ps)    252150532D41646F6265
Adobe Acrobat (pdf)    255044462D312E
Quicken (qdf)    AC9EBD8F
Windows Password (pwl)    E3828596
ZIP Archive (zip)    504B0304
RAR Archive (rar)    52617221
Wave (wav)    57415645
AVI (avi)    41564920
Real Audio (ram)    2E7261FD
Real Media (rm)    2E524D46
MPEG (mpg)    000001BA
MPEG (mpg)    000001B3
Quicktime (mov)    6D6F6F76
Windows Media (asf)    3026B2758E66CF11
MIDI (mid)    4D546864
"""

# 字节码转16进制字符串
def bytes2hex(bytes):
    num = len(bytes)
    hexstr = u""
    for i in range(num):
        t = u"%x" % bytes[i]
        if len(t) % 2:
            hexstr += u"0"
        hexstr += t
    return hexstr.upper()


#图片类型
def pictype(picobj):

    filetype=None
    data=picobj.read(10).encode("hex")
    print data
    if data.startswith("ffd8ffe0"):
        filetype="jpg"
    elif data.startswith("474946"):
        filetype="gif"
    elif data.startswith("424d"):
        filetype="bmp"
    elif data.startswith('89504e470d0a1a0a'):
        filetype="png"
    return filetype


# 获取文件类型
def filetype(filename):

    binfile = open(filename, 'rb')    #必需二制字读取
    tl = typeList()
    ftype = 'unknown'
    for hcode in tl.keys():
        numOfBytes = len(hcode) / 2   #需要读多少字节
        binfile.seek(0)               #每次读取都要回到文件头，不然会一直往后读取
        hbytes = struct.unpack_from("B"*numOfBytes, binfile.read(numOfBytes)) # 一个 "B"表示一个字节
        f_hcode = bytes2hex(hbytes)
        if f_hcode == hcode:
            ftype = tl[hcode]
            break
    binfile.close()
    return ftype


# 判断是否是合法的邀请码
def is_valid_invite_code(code):
    # if re.match('^[1-9a-zA-Z]*$', code) and len(code) == 6:
    if len(code) >= 4:
        return True
    return False


if __name__ == '__main__':
    #print filetype("/home/long/Downloads/王金龙-简历.doc")
    print is_valid_password("ak23UI!#")
