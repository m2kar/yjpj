# -*- coding: utf-8 -*- 
"""

"""
#   @Time:  2017/6/23 9:49
#   @Author:still_night@163.com
#   @File:  process_order.py
import time
from random import randint
import  JwUser,const,send_mail
from log import logging

def process_order(info):
    # info=q.get()

    stuid=info['student_id']
    passwd=info['passwd']
    email=info['email']
    user=JwUser.JwglUser(stuid,passwd)
    time.sleep(randint(10,30))
    try:
        user.check_user_passwd()
    except JwUser.const.LoginError:
        logging.error( "password Wrong %s %s"%(stuid,passwd))
        send_mail.send_check_fail(email,stuid,passwd)
    else:
        logging.info("password true %s %s"%(stuid,passwd))
        # try:
        #     send_mail.send_check_ok(email, stuid, passwd)
        # except Exception,e:
        #     logging.error(e.message)
        user.pj_all_teacher()
        logging.info("comment success ,start send mail %s %s"%(stuid,passwd))
        time.sleep(randint(10,40))
        try:
            send_mail.send_comment_ok(email, stuid, passwd)
        except Exception,e:
            logging.error(e.message)


