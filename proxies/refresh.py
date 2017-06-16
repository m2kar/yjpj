#! python3
#coding=utf-8
"""

@File:  refresh.py
@Author: still_night
@Contact:still_night@163.com
@Date: 2017/2/25
@Time: 11:44
@License: GPL
"""

import requests
import sqlite3
import logging
from bs4 import BeautifulSoup
from collections import OrderedDict
import datetime

import const



def refresh():
    url=const.server_url
    for i in range(const.page_counts):
        try:
            res=requests.get('%s/%d'%(url,i),headers=const.headers)
        except ConnectionError:
            pass
        else:
            process_respose(res)

def str_to_stamp(time_str):
    return int(datetime.datetime.strptime(time_str, '%y-%m-%d %H:%M').timestamp())

def process_respose(res):
    if res.status_code==200:
        res.encoding='utf-8'
        soup=BeautifulSoup(res.text,'html.parser')
        elemlist=soup.select('#ip_list > tr')
        serverlist=[]
        for each in elemlist[1:]:
            each_detail_list=each.select('td')
            serverlist.append(dict(
                ip=each_detail_list[1].text,
                port=each_detail_list[2].text,
                proxy_type=each_detail_list[5].text,
                time=each_detail_list[9].text,
                time_stamp=str_to_stamp(each_detail_list[9].text)
            ))
        save_server_list(serverlist)

def save_server_list(serverlist):

    pass



def main():
    refresh()


if __name__ == '__main__':
    main()