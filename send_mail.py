# -*- coding: utf-8 -*- 
"""

"""
#   @Time:  2017/6/23 1:43
#   @Author:still_night@163.com
#   @File:  send_mail.py
from __future__ import unicode_literals

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header

import const
from log import logging
import time


def login():
    server = None
    retry = 5
    while retry > 0:
        retry -= 1
        try:
            server = smtplib.SMTP(const.SMTPHOST)
            server.login(const.MAILUSERNAME, const.MAILPASSWORD)
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


def send(address, subject, content, From=const.MAILUSERNAME + "@sina.com"):
    s = login()
    # server=minfo['server']
    message = MIMEMultipart('alternative')
    message.set_charset('utf8')
    message['FROM'] = From
    message['Subject'] = Header(subject.encode('utf-8'), 'UTF-8').encode()
    _attach = MIMEText(content.encode('utf-8'), _charset='utf-8')
    message.attach(_attach)
    retry = 5
    while retry > 0:
        retry -= 1
        try:
            s.sendmail(From, [address, ], message.as_string())
        except (smtplib.SMTPServerDisconnected, smtplib.SMTPConnectError,
                smtplib.SMTPAuthenticationError, smtplib.SMTPHeloError, smtplib.SMTPException), e:
            logging.warn("邮件失败,正在重试: %s %s %s" % (address, content, e))
            login()
        else:
            break
    s.close()
    # server.sendmail(From,[address,],message)


def send_check_fail(adress, stu_id, password):
    subject = u"[医大一键评教]用户名密码验证失败 %s" % stu_id
    content = u"""

    你好:

        我是医大一键评教机器人,我们已经收到您的信息,但是发现您的教务系统用户名密码有错误.
        学号: %s  
        密码:%s
        请您自行登陆教务系统验证,然后将正确的用户名和密码通过电子邮件回复给我
        教务系统网址:http://202.118.40.67/jwglxt/xtgl/dl_loginForward.html
        我的邮箱是: yjpj_service@sina.com
        我的QQ/微信:531903884
        感谢您的支持!
        欢迎将此服务分享给您的朋友圈和空间.
        订单页网址:http://stillnight.mikecrm.com/wI47y1z
    """ % (stu_id, password)
    send(adress, subject, content)

def send_check_ok(adress, stu_id, password):
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

        教务系统网址:http://202.118.40.67/jwglxt/xtgl/dl_loginForward.html
        我的邮箱是: yjpj_service@sina.com 

        欢迎将此服务分享给您的朋友圈和空间.
        订单页网址:http://stillnight.mikecrm.com/wI47y1z
        感谢您的支持!

    """ % (stu_id, password)
    send(adress, subject, content)


def send_comment_ok(adress, stu_id, password):
    subject = u"[医大一键评教]教务评价已成功 %s" % stu_id
    content = u"""
    你好:

        我是医大一键评教机器人,  我们已经成功帮您完成了教务系统的评价.
        学号: %s  
        密码: %s
        有任何问题可以通过邮箱,微信或QQ 联系我.
        我的邮箱是: yjpj_service@sina.com
        我的QQ/微信是: 531903884
        欢迎将此服务分享给您的朋友圈和空间.
        网址:https://stillnight.mikecrm.com/wI47y1z
        感谢您的支持!

    """ % (stu_id, password)
    send(adress, subject, content)


login()
if __name__ == '__main__':
    # send_check_fail("still_night@163.com","1","2")
    # send_check_ok("still_night@163.com", "1", "2")
    send_comment_ok("531903884@qq.com", "1", "2")
    # minfo['server'].close()

    # FROM = 'yjpj_service@sina.com'
    # TO = ["still_night@163.com"] # must be a list
    # SUBJECT = "Hello!"
    # TEXT = "This message was sent with Python's smtplib."
    # # Prepare actual message
    # message = """\
    # From: %s
    # To: %s
    # Subject: %s
    # %s
    # """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
    #
    # # Send the mail
    #
    # login()
    # server=minfo['server']
    # server.sendmail(FROM, TO, message)
    # server.quit()