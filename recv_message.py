#! python3
#coding=utf-8
"""

@File:  recv_message.py
@Author: still_night
@Contact:still_night@163.com
@Date: 2017/6/16
@Time: 13:28
@License: GPL
"""

from __future__ import unicode_literals

import getpass, sys,email
import imapclient
from lxml import etree
from io import StringIO
from backports import ssl
import re

class const:
    HOST='imap.sina.com'
    USERNAME="yjpj_service"
    PASSWORD="rzq123"
    pattern = re.compile("您的表单 .*? 收到一笔新的付款 | 麦客CRM")

context = imapclient.create_default_context()
context.check_hostname = False
context.verify_mode = ssl.CERT_NONE
server = imapclient.IMAPClient(const.HOST, use_uid=True, ssl=True, ssl_context=context)
server.login(const.USERNAME,const.PASSWORD)
server.select_folder('INBOX',readonly=True)
result=server.search('UNSEEN')
msgdict=server.fetch(result,['BODY.PEEK[]'])
for message_id,message in msgdict.items():
    e= email.message_from_string(message['BODY[]'])
    subject=e.get("subject")
    h=email.Header.Header(subject)
    dh=email.Header.decode_header(h)
    print("subject %s "%subject)
    print("from:%s"% email.utils.parseaddr(e.get("from"))[1])
    print("to:%s"% email.utils.parseaddr(e.get("to"))[1] )
    #subject = email.header.make_header(email.header.decode_header(e['SUBJECT']))
    #mail_from= email.header.make_header(email.header.decode_header(e['From']))

    maintype=e.get_content_maintype()
    if maintype=='multipart':
        for part in e.get_payload():
            if part.get_content_maintype()=='text':
                mail_content=part.get_payload(decode=True).strip()
    elif maintype=='text':
        mail_content=e.get_payload(decode=True).strip()

    assert isinstance(mail_content, str)
    mail_content=mail_content.decode('utf-8')

    #

    parser = etree.HTMLParser()
    tree = etree.parse(StringIO(mail_content), parser)
    #result = etree.tostring(tree.getroot(), pretty_print=True, method="html")
    root=tree.getroot()
    mailbody = root.xpath('//tr[@class="mk_mailBody"]/td/table')[0]
    form_title=mailbody.xpath("tr/td/p[2]/span")[0].text  #表单名
    form_id=mailbody.xpath("tr[2]/td/table/tr/td[1]/span")[0].text #序号  '#21'
    submit_time=mailbody.xpath("tr[2]/td/table/tr/td[4]/span")[0].text #提交时间  '2017-05-19 13:34:43'
    order_id=mailbody.xpath("tr[3]/td/table/tr/td[1]/table/tr/td/p")[0].text.strip().split(u"：")[1]  #订单号  麦客订单号：IFP-CN101-1705190004110819
    payment_id=mailbody.xpath("tr[3]/td/table/tr/td[1]/table/tr/td/p[2]")[0].text.strip().split(u"：")[1] #支付交易号 支付平台交易号：2017051921001004380237658492
    price=float(mailbody.xpath("tr[3]/td/table/tr[3]/td/p/span[2]")[0].text[2:])  #价格
    stu_id=mailbody.xpath("tr[4]/td/table/tr[1]/td[2]")[0].text.strip() #学号
    passwd=mailbody.xpath("tr[4]/td/table/tr[2]/td[2]")[0].text.strip()
    email=mailbody.xpath("tr[4]/td/table/tr[3]/td[2]/div/p")[0].text.strip()
    print(mail_content)


class mailbox():
    def __init__(self,hostname=const.HOST):
        context = imapclient.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        self.server = imapclient.IMAPClient(hostname, use_uid=True, ssl=True, ssl_context=context)
    def login(self,username=const.USERNAME,password=const.PASSWORD):
        self.server.login(username,passwd)
        server.select_folder('mike')


    def recv(self):
        result = server.search('UNSEEN')
        msgdict = server.fetch(result, ['BODY.PEEK[]'])
        for message_id, message in msgdict.items():
            e = email.message_from_string(message['BODY[]'])
            # subject = e.get("subject")
            # h = email.Header.Header(subject)
            # dh = email.Header.decode_header(h)
            # dh[0][0]
            subject=email.Header.decode_header(email.Header.Header(e.get("subject")))[0][0]
            sender = email.utils.parseaddr(e.get("from"))[1]
            print("subject %s " % subject)
            print("from:%s" %  sender)
            print("to:%s" % email.utils.parseaddr(e.get("to"))[1])
            if const.pattern.match(subject) and sender.find("mikecrm1")>=0:
                maintype = e.get_content_maintype()
                if maintype == 'multipart':
                    for part in e.get_payload():
                        if part.get_content_maintype() == 'text':
                            mail_content = part.get_payload(decode=True).strip()
                elif maintype == 'text':
                    mail_content = e.get_payload(decode=True).strip()
                mail_content = mail_content.decode('utf-8')
                if self.save(mail_content):
                    self.server.set_flags(message_id,[imapclient.SEEN])

    def parser(self,content):
        info={}
        parser = etree.HTMLParser()
        tree = etree.parse(StringIO(content), parser)
        # result = etree.tostring(tree.getroot(), pretty_print=True, method="html")
        root = tree.getroot()
        mailbody = root.xpath('//tr[@class="mk_mailBody"]/td/table')[0]
        info['form_title'] = mailbody.xpath("tr/td/p[2]/span")[0].text.strip()  # 表单名
        info['form_id'] = int(mailbody.xpath("tr[2]/td/table/tr/td[1]/span")[0].text[1:] ) # 序号  '#21'
        info['submit_time'] = mailbody.xpath("tr[2]/td/table/tr/td[4]/span")[0].text.strip()  # 提交时间  '2017-05-19 13:34:43'
        info['order_id'] = mailbody.xpath("tr[3]/td/table/tr/td[1]/table/tr/td/p")[0].text.strip().split(u"：")[1]  # 订单号  麦客订单号：IFP-CN101-1705190004110819
        payment_id = mailbody.xpath("tr[3]/td/table/tr/td[1]/table/tr/td/p[2]")[0].text.strip().split(u"：")[1]  # 支付交易号 支付平台交易号：2017051921001004380237658492
        price = float(mailbody.xpath("tr[3]/td/table/tr[3]/td/p/span[2]")[0].text[2:])  # 价格
        stu_id = mailbody.xpath("tr[4]/td/table/tr[1]/td[2]")[0].text.strip()  # 学号
        passwd = mailbody.xpath("tr[4]/td/table/tr[2]/td[2]")[0].text.strip()
        email = mailbody.xpath("tr[4]/td/table/tr[3]/td[2]/div/p")[0].text.strip()

    def save(self,content):

        return True

def main():
    pass


if __name__ == '__main__':
    main()