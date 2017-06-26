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

import process_order, recv_info
from log import logging


def loop_process_order(q):
    """循环接收队列Q的信息并处理,已经启用,多线程/进程编程可以采用这个"""
    while True:
        logging.debug("q.get start")
        info=q.get()
        logging.debug("q.get end  %s"%info['student_id'])
        logging.info(u"开始处理订单:获取到 " + str(info[u'student_id']))
        process_order.process_order(info)
        sleep(15*random())


def manage():
    """管理 接收信息和处理信息"""
    logging.info("****start manager  *********")
    logging.debug(const.sys.path)
    q=Queue.Queue()
    m = recv_info.Mailbox(queue=q)
    while True:
        m.recv_to_queue(q)
        while not q.empty():
            info = q.get()
            logging.debug("q.get end  %s" % info['student_id'])
            logging.info(u"开始处理订单:获取到 " + str(info[u'student_id']))
            process_order.process_order(info)
            sleep(10 * random())
        sleep(60*random())
        # loop_process_order(q)
    # pool.map(loop_process_order,[q for i in range(num)])


if __name__ == '__main__':
    t = 0
    while True:
        try:
            manage()
        except Exception, e:
            logging.error(e)
        finally:
            # 如果出错到一定程度就发送日志
            t += 1
            if t % 5 == 0:
                import send_logs
                send_logs.send_log()
