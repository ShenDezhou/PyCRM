#-*- coding=utf-8 -*-
__author__ = 'wangjinlong@asiencredit.com'

from Crypto.Cipher import AES
import sys
import base64
sys.path.insert(0, "..")
from config import settings
import hashlib, time, datetime
import short_url
from urlparse import parse_qs, urlparse

BS = AES.block_size
pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS)
unpad = lambda s: s[0:-ord(s[-1])]
key = settings['cipher']
cipher = AES.new(key)


def encrypt_pwd(rawstr):

    """
    加密
    :param rawstr:明文
    :return: 密文
    """
    result = cipher.encrypt(pad(rawstr))
    result = base64.b64encode(result)

    result = hashlib.md5(result).hexdigest().upper()
    return result

# def decrypt(ciphertext):
#
#     """
#     解密
#     :param ciphertext: 密文
#     :return: 明文
#     """
#     result = base64.b64decode(ciphertext)
#     result = unpad(cipher.decrypt(result))
#     return result

def generate_encrypt_url_key(k, t):
    return encrypt_pwd(k + t + settings['cookie_secret'])

def generate_encrypt_url(path, k, t = None):
    if not t:
        t = str(time.time())
    ps = parse_qs(urlparse(path).query, keep_blank_values=True)
    _k = ps[k][0] #path.split(k + '=')[-1].split('&')[0].replace('#', '')
    s = generate_encrypt_url_key(_k, t)
    return path + '&_kk=' + k + '&_tt=' + t + '&_ss=' + s

def generate_short_url(url, handler):
    s_url = short_url.encode_url(datetime.datetime.now().microsecond, min_length=5)
    handler.set_cache(s_url, url, timeout = 3600 * 24 * 15)
    return handler.config['short_host_url'] + s_url

def generate_short_encrypt_url(url, k, t = None, handler = None):
    e_url = generate_encrypt_url(url, k, t)
    return generate_short_url(e_url, handler)


def assert_encrypt_url(path):
    ps = parse_qs(urlparse(path).query, keep_blank_values=True)
    k = ps['_kk'][0] if '_kk' in ps else '' #path.split('_kk=')[-1].split('&')[0].replace('#', '')
    t = ps['_tt'][0] if '_tt' in ps else '' #path.split('_tt=')[-1].split('&')[0].replace('#', '')
    s = ps['_ss'][0] if '_ss' in ps else '' #path.split('_ss=')[-1].split('&')[0].replace('#', '')
    _k = ps[k][0] if k in ps else '' #path.split(k + '=')[-1].split('&')[0].replace('#', '')
    if k and t and s and _k and generate_encrypt_url_key(_k, t) == s:
        return True
    return False




if __name__ == '__main__':
    print encrypt_pwd('10001test01')
    print encrypt_pwd('10002test02')
    print encrypt_pwd('10003test03')
    print encrypt_pwd('10004test04')
    print encrypt_pwd('10005test05')
    print encrypt_pwd('123456')