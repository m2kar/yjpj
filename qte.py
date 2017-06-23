# -*- coding: utf-8 -*- 
"""

"""
#   @Time:  2017/6/23 0:25
#   @Author:still_night@163.com
#   @File:  qte.py

from multiprocessing import Process,Queue,Pool,Manager
from time import sleep
from random import random

def f(q):
    i=0
    while True:
        i=i+1
        r=random()
        q.put([i,r])
        sleep(r)

def g(q,n):
    print("worker",n,"   ",q.get())

if __name__ == '__main__':
    m=Manager()
    q=m.Queue()
    p=Process(target=f,args=(q,))
    p.start()
    num=5
    pool=Pool(processes=num)
    i=1
    while True:
        i=i+1
        # print(q.get())
        pool.apply_async(g,(q,i))

        # sleep(random())

    # w=[]
    # for i in range(num):
    #     p2=Process(target=g,args=(q,i,))
    #     w.append(p2)
    #     p2.start()
    # p.join()


