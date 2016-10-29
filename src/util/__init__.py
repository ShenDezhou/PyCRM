# -*- coding: utf-8 -*-  
from config import settings
import os, os.path
import json, datetime, time, decimal
import zipfile
import numpy as np
import numpy

DPATH = settings['original_file_path']

def alioss_file_util(optype, fpath, content = ""):
    from oss.oss_api import OssAPI
    bucketname = settings["oss_bucket_name"]
    endpoint = settings["oss_endpoint"]
    accessKeyId, accessKeySecret = settings['oss_accessKeyId'], settings['oss_accessKeySecret']
    oss = OssAPI(endpoint, accessKeyId, accessKeySecret)
    if optype == 'read':
        res = oss.get_object(bucketname, fpath)
        return res.read() or ""
    elif optype == 'write':
        res = oss.put_object_from_string(bucketname, fpath, content)
        return True
    return ''

def to_timestamp(dt):
    return time.mktime(dt.timetuple())

class ComplexEncoder(json.JSONEncoder):
     def default(self, obj):
        # print 'obj', obj, isinstance(obj, bool), type(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, numpy.bool_):
            return True if obj else False
        elif isinstance(obj, datetime.datetime) or isinstance(obj, datetime.date):
            return str(obj)
        elif isinstance(obj, decimal.Decimal):
            return float(obj)
        return json.JSONEncoder.default(self, obj)

def dump_json(res, indent = None):
    return json.dumps(eval(res) if isinstance(res, str) else res, cls=ComplexEncoder, ensure_ascii=False, indent = indent)

def get_or_create_path(fpath):
    if fpath.find('/') > 0:
        fpath = fpath.split('/')[0] + '.' + fpath.split('.')[-1]
    path = DPATH
    for p in fpath[:3]:
        path = path + p + '/'
        if not os.path.exists(path):
            os.mkdir(path)
    return str(path + fpath)


def write_file(fpath, content):
    if fpath.find('/') > 0:
        fpath = fpath.split('/')[0] + '.' + fpath.split('.')[-1]

    if settings['production'] and 'oss_enabled' in settings and settings['oss_enabled']:
        return alioss_file_util('write', fpath, content)

    path = get_or_create_path(fpath)
    f = open(path, 'wb')
    f.write(content)
    f.close()    


def read_file(fpath):
    if fpath.find('/') > 0:
        fpath = fpath.split('/')[0] + '.' + fpath.split('.')[-1]

    if settings['production'] and 'oss_enabled' in settings and settings['oss_enabled']:
        return alioss_file_util('read', fpath)

    path = DPATH + '/'.join(fpath[:3]) + '/' + fpath
    if os.path.exists(path):
        f = open(path, 'rb')
        content = f.read()
        f.close()
        return content

    return "" 

def remove_file(fpath):
    if fpath.find('/') > 0:
        fpath = fpath.split('/')[0] + '.' + fpath.split('.')[-1]
    path = DPATH + '/'.join(fpath[:3]) + '/' + fpath
    if os.path.exists(path):
        os.remove(path)
        return True
    return False

def is_file_existed(fpath):
    if fpath.find('/') > 0:
        fpath = fpath.split('/')[0] + '.' + fpath.split('.')[-1]
    path = DPATH + '/'.join(fpath[:3]) + '/' + fpath
    if os.path.exists(path):
        return True
    return False

def get_file_path(fpath):
    if fpath.find('/') > 0:
        fpath = fpath.split('/')[0] + '.' + fpath.split('.')[-1]
    path = DPATH + '/'.join(fpath[:3]) + '/' + fpath
    if os.path.exists(path):
        return path
    return ""

def zip_dir(dirname,zipfilename):
    filelist = []
    if os.path.isfile(dirname):
        filelist.append(dirname)
    else:
        for root, dirs, files in os.walk(dirname):
            for name in files:
                filelist.append(os.path.join(root, name))

    zf = zipfile.ZipFile(zipfilename, "w", zipfile.zlib.DEFLATED)
    for tar in filelist:
        arcname = tar[len(dirname):]
        #print arcname
        zf.write(tar, arcname)
    zf.close()


def unzip_file(zipfilename, unziptodir):
    if not os.path.exists(unziptodir):
        os.mkdir(unziptodir, 0777)
    zfobj = zipfile.ZipFile(zipfilename)
    for name in zfobj.namelist():
        name = name.replace('\\', '/')

        if name.endswith('/'):
            os.mkdir(os.path.join(unziptodir, name))
        else:
            ext_filename = os.path.join(unziptodir, name)
            ext_dir= os.path.dirname(ext_filename)
            if not os.path.exists(ext_dir):
                os.mkdir(ext_dir, 0777)
            outfile = open(ext_filename, 'wb')
            outfile.write(zfobj.read(name))
            outfile.close()


def unrar_file(rarfilename, unrartodir):
    if not os.path.exists(unrartodir):
        os.mkdir(unrartodir, 0777)
    zfobj = zipfile.ZipFile(rarfilename)
    for name in zfobj.namelist():
        name = name.replace('\\', '/')

        if name.endswith('/'):
            os.mkdir(os.path.join(unrartodir, name))
        else:
            ext_filename = os.path.join(unrartodir, name)
            ext_dir= os.path.dirname(ext_filename)
            if not os.path.exists(ext_dir):
                os.mkdir(ext_dir, 0777)
            outfile = open(ext_filename, 'wb')
            outfile.write(zfobj.read(name))
            outfile.close()