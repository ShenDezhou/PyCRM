# -*- coding: utf-8 -*-
import time
import random
import string
import hashlib
import json
import requests
import logging
class Sign:
    def __init__(self, appId, appSecret, url, handler):
        self.appId = appId
        self.appSecret = appSecret
        self.handler = handler
        self.jsapi_ticket_key = 'jsapi_ticket_value'
        self.jsapi_access_token_key = 'jsapi_access_token_token'

        self.ret = {
            'nonceStr': self.__create_nonce_str(),
            'jsapi_ticket': self.getJsApiTicket(),
            'timestamp': self.__create_timestamp(),
            'url': url
        }

    def __create_nonce_str(self):
        return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(15))

    def __create_timestamp(self):
        return int(time.time())

    def sign(self):
        string = '&'.join(['%s=%s' % (key.lower(), self.ret[key]) for key in sorted(self.ret)])
        print string
        self.ret['signature'] = hashlib.sha1(string).hexdigest()
        self.ret['appid'] = self.appId
        return self.ret

    def getJsApiTicket(self):
        data = self.handler.get_cache(self.jsapi_ticket_key) #json.loads(open('jsapi_ticket.json').read())
        jsapi_ticket = data #data['jsapi_ticket']
        if not jsapi_ticket:
            url = "https://api.weixin.qq.com/cgi-bin/ticket/getticket?type=jsapi&access_token=%s" % (self.getAccessToken())
            response = requests.get(url, verify=False)
            jsapi_ticket = json.loads(response.text)['ticket']
            # data['jsapi_ticket'] = jsapi_ticket
            # data['expire_time'] = int(time.time()) + 7000
            self.handler.set_cache(self.jsapi_ticket_key, jsapi_ticket, 7000)
            # fopen = open('jsapi_ticket.json', 'w')
            # fopen.write(json.dumps(data))
            # fopen.close()
        return jsapi_ticket

    def getAccessToken(self):
        data = self.handler.get_cache(self.jsapi_access_token_key) #json.loads(open('access_token.json').read())
        access_token = data #data['access_token']
        if not access_token:
            url = "https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=%s&secret=%s" % (self.appId, self.appSecret)
            response = requests.get(url, verify=False)
            access_token = json.loads(response.text)['access_token']
            self.handler.set_cache(self.jsapi_access_token_key, access_token, 7000)
            # data['access_token'] = access_token
            # data['expire_time'] = int(time.time()) + 7000
            # fopen = open('access_token.json', 'w')
            # fopen.write(json.dumps(data))
            # fopen.close()
        return access_token

    def clearCache(self):
        access_token = self.handler.get_cache(self.jsapi_access_token_key) 
        self.handler.set_cache(self.jsapi_access_token_key, access_token, 1)
        print self.jsapi_access_token_key+' clear.'
        

if __name__ == '__main__':
    # 注意 URL 一定要动态获取，不能 hardcode
    appId = 'wx9aaaaaaaaaaaaa'
    appSecret = 'a******************'
    sign = Sign(appId, appSecret, 'http://example.com')
    print sign.sign()