#coding=utf-8

__author__ = 'karldoenitz'

import tornado

# from tornadomail import send_mail
# from tornadomail.backends.smtp import EmailBackend
# from tornadomail.message import EmailMessage
# import tornadomail
import urllib
import base64
import smtplib
import json
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import thread, sys
sys.path.insert(0, "..")
from config import settings

# from smtplib import SMTPException, SMTPAuthenticationError
# import string
# import base64
# import sspi
# # NTLM Guide --  CodeGo.net 
# SMTP_EHLO_OKAY = 250
# SMTP_AUTH_CHALLENGE = 334
# SMTP_AUTH_OKAY = 235
# def asbase64(msg):
#     return string.replace(base64.encodestring(msg), '\n', '')
# def connect_to_exchange_as_current_user(smtp):
#     """Example:
#     >>> import smtplib
#     >>> smtp = smtplib.SMTP("my.smtp.server")
#     >>> connect_to_exchange_as_current_user(smtp)
#     """
#     # Send the SMTP EHLO command
#     code, response = smtp.ehlo()
#     if code != SMTP_EHLO_OKAY:
#         raise SMTPException("Server did not respond as expected to EHLO command")
#     sspiclient = sspi.ClientAuth('NTLM')
#     # Generate the NTLM Type 1 message
#     sec_buffer=None
#     err, sec_buffer = sspiclient.authorize(sec_buffer)
#     ntlm_message = asbase64(sec_buffer[0].Buffer)
#     # Send the NTLM Type 1 message -- Authentication Request
#     code, response = smtp.docmd("AUTH", "NTLM " + ntlm_message)
#     # Verify the NTLM Type 2 response -- Challenge Message
#     if code != SMTP_AUTH_CHALLENGE:
#         raise SMTPException("Server did not respond as expected to NTLM negotiate message")
#     # Generate the NTLM Type 3 message
#     err, sec_buffer = sspiclient.authorize(base64.decodestring(response))
#     ntlm_message = asbase64(sec_buffer[0].Buffer)
#     # Send the NTLM Type 3 message -- Response Message
#     code, response = smtp.docmd("", ntlm_message)
#     if code != SMTP_AUTH_OKAY:
#         raise SMTPAuthenticationError(code, response)


class CCSendMail:
    def __init__(self, config):
        self.__smtp = smtplib.SMTP(config['mail_smtp_server'], int(config['mail_smtp_port']))
        self.__subject = None
        self.__content = None
        self.__from = None
        self.__to = []
        self.__style = 'html'
        self.__charset = 'gb2312'
        self.username = config['noreply_mail_address']
        self.password = config['noreply_mail_password']
        self.fromAlias = config['noreply_mail_name']
        self.from2 = ''

    def close(self):
        try:
            self.__smtp.quit()
        except Exception, e:
            pass

    def setFromAlias(self, alias):
        self.fromAlias = alias

    def setStyle(self, style):
        self.__style = style

    def setFrom2(self, from2):
        self.from2 = from2

    def setSubject(self, subject):
        self.__subject = subject

    def setContent(self, content):
        self.__content = content

    def setFrom(self, address):
        self.__from = address

    def addTo(self, address):
        self.__to.append(address)

    def setCharset(self, charset):
        self.__charset = charset

    def send(self):
        #try:
        # self.__smtp.set_debuglevel(1)

        # self.__smtp.ehlo()
        # self.__smtp.starttls()
        # self.__smtp.ehlo
        
        # login if necessary
        if self.username and self.password:
            self.__smtp.login(self.username, self.password)

        msgRoot = MIMEMultipart('related')
        msgRoot['Subject'] = self.__subject
        aliasB6 = base64.encodestring(self.fromAlias.encode(self.__charset))
        if len(self.from2) == 0:
            msgRoot['From'] = "=?%s?B?%s?=%s" % (self.__charset, aliasB6.strip(), self.__from)
        else:
            msgRoot['From'] = "%s" % (self.from2)
        msgRoot['To'] = ";".join(self.__to)

        msgAlternative = MIMEMultipart('alternative')
        msgRoot.attach(msgAlternative)

        msgText = MIMEText(self.__content, self.__style, self.__charset)
        msgAlternative.attach(msgText)

        self.__smtp.sendmail(self.__from, self.__to, msgRoot.as_string())
        return True
        # except Exception, e:
        #     print "Error ", e
        #     return False

    def send_bcc(self):
        if self.username and self.password:
            self.__smtp.login(self.username,self.password)

        msgRoot = MIMEMultipart('related')
        msgRoot['Subject'] = self.__subject
        aliasB6 = base64.encodestring(self.fromAlias.encode(self.__charset))
        if len(self.from2) == 0:
            msgRoot['From'] = "=?%s?B?%s?=%s" % (self.__charset, aliasB6.strip(), self.__from)
        else:
            msgRoot['From'] = "%s" % (self.from2)
        msgRoot['Bcc'] = ";".join(self.__to)

        msgAlternative = MIMEMultipart('alternative')
        msgRoot.attach(msgAlternative)

        msgText = MIMEText(self.__content, self.__style, self.__charset)
        msgAlternative.attach(msgText)

        self.__smtp.sendmail(self.__from, self.__to, msgRoot.as_string())
        return True


    def clearRecipient(self):
        self.__to = []

    # 给单个人发送邮件
    def sendhtml(self, address, title, content):
        self.setStyle('html')
        self.setFrom("<%s>" % self.username)
        # if not isinstance(content, str):
        content = content.encode('gb18030')
        self.addTo(address)
        self.setSubject(title)
        self.setContent(content)
        ret = self.send()
        self.close()
        return ret

    #群发邮件
    def sendmorehtml(self, addressList, title, content):
        self.setStyle('html')
        self.setFrom("<%s>" % self.username)
        if not isinstance(content, str):
            content = content.encode('gb18030')
        for address in addressList:
            self.addTo(address)
        self.setSubject(title)
        self.setContent(content)
        ret = self.send()
        self.close()
        return ret

    def sendmorehtml_bcc(self, addressList, title, content):
        '''以bcc(暗送)模式来群发邮件'''
        self.setStyle('html')
        self.setFrom("<%s>" % self.username)
        if not isinstance(content, str):
            content = content.encode('gb18030')
        for address in addressList:
            self.addTo(address)
        self.setSubject(title)
        self.setContent(content)
        ret = self.send_bcc()
        self.close()
        return ret

if __name__ == '__main__':
    send = CCSendMail()
    send.sendhtml('250380149@qq.com', u'test艾',u'邮件====内容')
    #send.sendMoreHtml([touser1@xx.com,touser2@xx.com],u'邮件标题',u'邮件内容')


#发送短信
@tornado.gen.coroutine
def send_message(phone, message, config):
    CDKET = config['noreply_sms_account']
    PASSWD = config['noreply_sms_password']
    url="https://api.infobip.com/sms/1/text/single"
    headers = {"Content-Type":"application/json","Accept":"application/json"}
    data =json.dumps({"from":"106909001236282","to":"86%s" % phone,"text": message.encode('utf-8')})
    print CDKET
    print PASSWD
    print url
    print headers
    print data
    request = tornado.httpclient.HTTPRequest(url,method='POST',headers=headers, body=data, auth_username=CDKET,auth_password=PASSWD)
    http_client = tornado.httpclient.AsyncHTTPClient()
    #url = config['noreply_sms_url'] % {'account': CDKET, 'password': PASSWD, 'phone': phone, 'message': urllib.quote_plus(message.encode('utf-8'))}
    response = yield http_client.fetch(request)
    raise tornado.gen.Return(response)


#发送邮件
def send_email(subject, account, message, config):

    # print subject, account

    send = CCSendMail(config)
    if type(account) == type([]):
        for a in account:
            send.sendhtml(a, subject, message)
    else:
        send.sendhtml(account, subject, message)

def send_more_email(subject, account_list, message, config):
    '''以bcc(暗送)模式来群发邮件'''
    send = CCSendMail(config)
    send.sendmorehtml_bcc(account_list,subject,message)

    # send = CCSendMail()
    # send.sendhtml(account, subject, message)
    #send_mail(subject, message, 'noreply@asiencredit.com', [account], callback=_finish, connection=EmailBackend('smtp.exmail.qq.com', 587, 'noreply@asiencredit.com', 'credit2014', True))
    # message = EmailMessage(subject, message, 'noreply@asiencredit.com', [account], connection=EmailBackend('smtp.exmail.qq.com', 587, 'noreply@asiencredit.com', 'credit2014', True))
    # message.send()



# if __name__ == '__main__':
#     #print tornadomail.__file__
#     send_email('你好', 'wangjinlong@asiencredit.com', 'WERTYUIOLDFGHJK<L>')


