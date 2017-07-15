# -*- coding: utf-8 -*- 
"""

"""
#   @Time:  2017/6/23 9:49
#   @Author:still_night@163.com
#   @File:  process_order.py
import time
from random import randint

import const
import JwUser, const, send_mail
from log import logging

def comment_order(stuid, passwd, email):
    u = JwUser.JwglUser(stuid, passwd)
    retry = 3
    while retry > 0:
        retry -= 1
        try:
            u.pj_all_teacher()
        except const.NetworkError, e:
            logging.error(" NetWorkerror  process_order pj_all_teacher retry:%s" % retry)

        else:
            logging.info("comment success ,start send mail %s %s %s" % (email, stuid, passwd))
            send_mail.send_comment_ok(email, stuid, passwd)
            u.req.close()
            break
    else:
        u.req.close()
        send_mail.send("ruizhiqing@foxmail.com", u"[一键评教]教务评价失败", u"%s \n%s \n%s" % (stuid, passwd, email))
        raise const.NetworkError


def check_password(stuid, passwd, email):
    u = JwUser.JwglUser(stuid, passwd)
    try:
        passwd_valid = u.is_password_valid()
    except const.NetworkError:
        logging.error("network err when check password const.NetworkError")
        errmsg = u"网络错误 %s %s %s" % (stuid, passwd, email)
        send_mail.send("ruizhiqing@foxmail.com", u"[一键评教]网络错误", errmsg)
        return
    finally:
        u.req.close()

    if not passwd_valid:
        logging.error("password Wrong %s %s" % (stuid, passwd))
        errmsg = u"密码失败 %s %s %s" % (stuid, passwd, email)
        send_mail.send("ruizhiqing@foxmail.com", u"[一键评教]密码验证失败", errmsg)
        send_mail.send_check_fail(email, stuid, passwd)
        return False
    else:
        logging.info("password valid %s %s" % (stuid, passwd))
        return True


def process_order(info):
    stuid = info['student_id']
    passwd = info['passwd']
    email = info['email']
    logging.info(u"start process_order %s %s %s" % (stuid, passwd, email))
    if not check_password(stuid, passwd, email):
        return
    else:
        comment_order(stuid, passwd, email)
