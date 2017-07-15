# -*- coding: utf-8 -*- 
"""

"""
#   @Time:  2017/6/23 10:02
#   @Author:still_night@163.com
#   @File:  manager.py

import const

import Queue
from time import sleep
from random import random

import process_order,recv_message
from log import logging


def loop_process_order(q):
    while True:
        logging.debug("q.get start")
        info=q.get()
        logging.debug("q.get end  %s"%info['student_id'])
        logging.info(u"开始处理订单:获取到 " + str(info[u'student_id']))
        process_order.process_order(info)
        sleep(15*random())

def manage():
    logging.info("****start manager  *********")
    logging.debug(const.sys.path)
    # m=Manager()
    # q=m.Queue()
    # p=Process(target=recv_message.recv_to_queue,args=(q,))
    # p.start()
    # num=3
    # pool=Pool(num)
    q=Queue.Queue()
    m=recv_message.Mailbox(queue=q)
    while True:
        m.recv_to_queue(q)
        while not q.empty():
            info = q.get()
            logging.debug("q.get end  %s" % info['student_id'])
            logging.info(u"开始处理订单:获取到 " + str(info[u'student_id']))
            process_order.process_order(info)
            sleep(10 )
        sleep(60)
        # loop_process_order(q)
    # pool.map(loop_process_order,[q for i in range(num)])


if __name__ == '__main__':
    t=0
    while True:

        try:
            manage()
        except Exception ,e:
            logging.error(e)
        finally:
            t += 1
            if t%5==0:
                import send_mail
                try:
                    f=open(const.INFOLOGFILE)
                except:
                    pass
                s=f.read()
                try:
                    send_mail.send("ruizhiqing@foxmail.com","[yjpj]infolog",s)
                except:
                    pass
