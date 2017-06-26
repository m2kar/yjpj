# -*- coding: utf-8 -*- 
"""
邮件发送模块,用于用户提交后成功或失败的信息反馈
"""
#   @Time:  2017/6/23 1:43
#   @Author:still_night@163.com
#   @File:  send_mail.py
from __future__ import unicode_literals

import  const

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header

from log import logging
import time

def login():
    server=None
    retry=5
    while retry>0:
        retry-=1
        try:
            server = smtplib.SMTP_SSL(const.SMTPHOST)
            server.login(const.SMTPUSERNAME, const.SMTPPASSWORD)
            # minfo['server']=server
        except smtplib.SMTPException:
            # if minfo['server'] :
            #     minfo['server'].close()
            logging.error("smtp登录失败 ,正在重试")
            time.sleep(3)
        else:
            break
    else:
        raise Exception("SMTP 登录失败")
    return server


def send(address,subject,content,From=const.SMTPFULLADDRESS):
    s=login()
    # server=minfo['server']
    message=MIMEMultipart('alternative')
    message.set_charset('utf8')
    message['FROM']=From
    message['Subject']=Header(subject.encode('utf-8'),'UTF-8').encode()
    _attach = MIMEText(content.encode('utf-8'), _charset='utf-8')
    message.attach(_attach)
    retry=5
    while retry>0:
        retry-=1
        try:
            s.sendmail(From,[address,],message.as_string())
        except (smtplib.SMTPServerDisconnected,smtplib.SMTPConnectError,
                smtplib.SMTPAuthenticationError,smtplib.SMTPHeloError,smtplib.SMTPException),e :
            logging.warn("邮件失败,正在重试: %s %s %s"%(address,content,e))
            login()
        else:
            break
    s.close()
    # server.sendmail(From,[address,],message)


def send_check_fail(adress,stu_id,password):
    subject=u"[医大一键评教] 密码错误 %s"% stu_id
    content=u"""
    
    你好:
        我是医大一键评教机器人,
        您的教务系统用户名密码有错误.
        学号: %s  
        密码:%s
        请您回复正确的账号密码给我
        我的QQ/微信 531903884
        感谢支持!
    """% (stu_id,password)
    send(adress,subject,content)

def send_check_ok(adress,stu_id,password):
    subject = u"[医大一键评教]订单已接收,正在评价 %s " % stu_id
    content = u"""

    你好:

        我是医大一键评教机器人,我们已经收到您的订单,正在马不停蹄帮您刷评价.
        请不要在最近登录教务系统后台.
        评价结束后将会有邮件通知您.
        学号: %s  
        密码:%s
        请您登录教务系统后台确认一下已经评价成功!!
        如果有任何问题可以通过邮箱联系我.
        
        我的邮箱是: yjpj_service@sina.com 
        
        欢迎将此服务分享给您的朋友圈和空间.
        感谢您的支持!
        
    """ % (stu_id, password)
    send(adress, subject, content)

def send_comment_ok(adress,stu_id,password):
    subject = u"[医大一键评教] 一键评教已成功 学号:%s" % stu_id
    content = u"""
    你好:
        医大一键评教,已经成功帮您完成了教务系统的评价. 
        有问题可以给我回复
        QQ/微信: 531903884
        感谢支持,欢迎分享给朋友!
    """
    send(adress, subject, content)

if __name__ == '__main__':
    send_comment_ok("531903884@qq.com", "1", "2")
