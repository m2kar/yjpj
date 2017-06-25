# -*- coding: utf-8 -*-
"""

@File:  recv_message.py
@Author: still_night
@Contact:still_night@163.com
@Date: 2017/6/16
@Time: 13:28
@License: GPL
"""

from __future__ import unicode_literals

import getpass, sys,email,re,time
import imapclient
from lxml import etree
from io import StringIO
from backports import ssl


# import database
import const
from log import logging

class mailbox():
    def __init__(self,queue=None):
        self.context = imapclient.create_default_context()
        self.context.check_hostname = False
        self.context.verify_mode = ssl.CERT_NONE
        self.queue=queue
        self.login()



    def login(self, username=const.MAILUSERNAME, password=const.MAILPASSWORD, hostname=const.IMAPHOST):
        self.username = username
        self.password = password
        while True:
            try:
                self.server = imapclient.IMAPClient(hostname, use_uid=True, ssl=True, ssl_context=self.context)
                self.server.login(self.username, self.password)
            except KeyboardInterrupt:
                raise
            except TypeError as e:
                logging.error("IMAP登录失败 " + str(e))
                time.sleep(10)
            except Exception as e:
                logging.error("IMAP登录失败 %s"%e.message)
            else:
                break


    def recv(self,parser):
        result = self.server.search('UNSEEN')
        msgdict = self.server.fetch(result, ['BODY.PEEK[]'])
        for message_id, message in msgdict.items():
            e = email.message_from_string(message['BODY[]'])
            subject=email.Header.decode_header(email.Header.Header(e.get("subject")))[0][0]
            sender = email.utils.parseaddr(e.get("from"))[1]
            maintype = e.get_content_maintype()
            if maintype == 'multipart':
                for part in e.get_payload():
                    if part.get_content_maintype() == 'text':
                        mail_content = part.get_payload(decode=True).strip()
            elif maintype == 'text':
                mail_content = e.get_payload(decode=True).strip()
            mail_content = mail_content.decode('utf-8')
            # logging.debug(mail_content)
            if self.save(mail_content,parser):
                self.server.set_flags(message_id,[imapclient.SEEN])

    def __parser_order_info(self,content):
        info={}
        parser = etree.HTMLParser()
        tree = etree.parse(StringIO(content), parser)
        # result = etree.tostring(tree.getroot(), pretty_print=True, method="html")
        root = tree.getroot()
        mailbody = root.xpath('//tr[@class="mk_mailBody"]/td/table')[0]
        info['form_title'] = mailbody.xpath("tr/td/p[2]/span")[0].text.strip()  # 表单名
        info['form_id'] = int(mailbody.xpath("tr[2]/td/table/tr/td[1]/table/tr/td[1]/span")[0].text[1:] ) # 序号  '#21'
        info['submit_date'] = mailbody.xpath("tr[2]/td/table/tr/td[1]/table/tr/td[4]/span")[0].text.strip()  # 提交时间  '2017-05-19 13:34:43'
        info['order_id'] = mailbody.xpath("tr[3]/td/table/tr/td[1]/table/tr/td[1]/p")[0].text.strip().split(u"\uff1a")[1]  # 订单号  麦客订单号：IFP-CN101-1705190004110819
        info['payment_id'] = mailbody.xpath("tr[3]/td/table/tr/td[1]/table/tr/td/p[2]")[0].text.strip().split(u"\uff1a")[1]  # 支付交易号 支付平台交易号：2017051921001004380237658492
        info['price'] = float(mailbody.xpath("tr[3]/td/table/tr[3]/td/p/span[2]")[0].text[2:])  # 价格
        info['student_id'] = mailbody.xpath("tr[4]/td/table/tr[1]/td[2]")[0].text.strip()  # 学号
        info['passwd'] = mailbody.xpath("tr[4]/td/table/tr[2]/td[2]")[0].text.strip()
        info['email'] = mailbody.xpath("tr[4]/td/table/tr[3]/td[2]/div/p")[0].text.strip()
        return info
    def __parser_work_order_info(self,content):
        info={}
        parser = etree.HTMLParser()
        tree = etree.parse(StringIO(content), parser)
        # result = etree.tostring(tree.getroot(), pretty_print=True, method="html")
        root = tree.getroot()
        valuetable = root.xpath('/html/body/table/tr/td/table/tr[2]/td/table/tr[3]/td/table')[0]
        info['student_id']=valuetable.xpath("tr[1]/td[2]")[0].text.strip()
        info['passwd']=valuetable.xpath("tr[2]/td[2]")[0].text.strip()
        info['email']=valuetable.xpath("tr[3]/td[2]/div/p")[0].text.strip()
        return info

    def save(self,content,parser):
        info=parser(content)
        logging.info("从邮件获取到学号:"+info['student_id'])
        if self.queue:
            logging.debug("学号存入队列"+info['student_id'])
            self.queue.put(info)
        return True

    def receive_payment(self):
        logging.debug("接收payment")
        self.server.select_folder("yjpj_payment")
        self.recv(self.__parser_order_info)


    def receive_workorder(self):
        logging.debug("接收work_order")
        self.server.select_folder("work_order")
        self.recv(self.__parser_work_order_info)

    def loop_recv(self):
        while True:
            self.recv()
            time.sleep(10)


def recv_to_queue(q):
    m=mailbox(q)
    logging.info("imap 登录成功")
    while True:
        logging.debug("开始接收邮件")
        try:
            m.receive_workorder()
            m.receive_payment()
        except KeyboardInterrupt:
            raise
        except Exception as e:
            try:
                m.server.logout()
            except Exception as e2:
                logging.error("imap logout error %s"%e2.message)
            m=mailbox(q)
        logging.debug("等待下一次接收邮件")
        time.sleep(10)

def main():
    import  Queue
    q=Queue.Queue()
    recv_to_queue(q)


if __name__ == '__main__':
    main()