# -*- coding: utf-8 -*- 
"""

"""
#   @Time:  2017/6/23 10:02
#   @Author:still_night@163.com
#   @File:  manager.py

from multiprocessing import Process,Queue,Pool,Manager
from time import sleep
from random import random

import const,process_order,recv_message
from log import logging


def loop_process_order(q):
    while True:
        logging.debug("q.get start")
        info=q.get()
        logging.debug("q.get end  %s"%info['student_id'])
        logging.info("处理订单:获取到" + str(info))
        process_order.process_order(info)

if __name__ == '__main__':
    m=Manager()
    q=m.Queue()
    p=Process(target=recv_message.recv_to_queue,args=(q,))
    p.start()
    # logging.debug("q.get start")
    # logging.debug("manger"+ str(q.get()))
    # logging.debug("q.get end")
    num=5
    # processList=[Process(target=loop_process_order,args=(q,)) for i in range(num)]
    pool=Pool(processes=num)
    # loop_process_order(q)
    pool.map(loop_process_order,[q for i in range(num)])
    # for i in range(num):
        # logging.debug("manger"+ str(q.get()['student_id']))
        # pool.apply_async(process_order.loop_process_order,(q,))
        # processList[i].start()