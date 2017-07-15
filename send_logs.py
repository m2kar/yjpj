# -*- coding: utf-8 -*- 
"""

"""
#   @Time:  2017/6/25 10:28
#   @Author:still_night@163.com
#   @File:  send_logs.py
import const
import sys

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
import send_mail
import os



def send_log():
    sender = const.SMTPFULLADDRESS
    receivers = ['531903884@qq.com']  # 接收邮件，可设置为你的QQ邮箱或者其他邮箱

    # 创建一个带附件的实例
    message = MIMEMultipart()
    message['From'] = Header("一键评教", 'utf-8')
    message['To'] = Header("程序猿", 'utf-8')
    subject = '[一键评教]日志'
    message['Subject'] = Header(subject, 'utf-8')

    # 邮件正文内容
    message.attach(MIMEText('日志', 'plain', 'utf-8'))

    for each in ("jwpj_info.log","jwpj.log","jwpj_err.log"):
        if os.path.exists(each):
            # 构造附件1，传送当前目录下的 test.txt 文件
            att = MIMEText(open('/root/yjpj/%s'%each, 'rb').read(), 'base64', 'utf-8')
            att["Content-Type"] = 'application/octet-stream'
            # 这里的filename可以任意写，写什么名字，邮件中显示什么名字
            att["Content-Disposition"] = 'attachment; filename="%s.txt"'%each
            message.attach(att)

    try:
        smtpObj = send_mail.login()
        smtpObj.sendmail(sender, receivers, message.as_string())
        print "邮件发送成功"
    except smtplib.SMTPException:
        print "Error: 无法发送邮件"

if __name__ == '__main__':
    if not sys.platform == "win32":
        send_log()

