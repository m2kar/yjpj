# -*- coding: utf-8 -*- 
"""

"""
#   @Time:  2017/6/17 21:22
#   @Author:still_night@163.com
#   @File:  database.py

import os
from sqlobject import *
import sys
import  logging


class const:
    if sys.platform == 'win32':
        HOST = "BADBOY-WIN10"
        PORT = "3306"
        USERNAME = "root"
        PASSWORD = "rzq123"
        DBNAME = 'jwpj'
        COLSIZ = 10
    else:
        HOST = "sqld.duapp.com"
        PORT = "3306"
        USERNAME = "c5fabd75d8a54144a1cc7336f7960103"
        PASSWORD = "5d53dba0ec894497b63e92a20eba1dd7"
        DBNAME = 'MTHqiJtNnmdwRPfgjhty'


HOST = const.HOST
PORT = const.PORT
USERNAME = const.USERNAME
PASSWORD = const.PASSWORD
DBNAME = const.DBNAME


class OrderTable(object):
    def __init__(self):
        import MySQLdb
        import _mysql_exceptions
        url = "mysql://%s:%s/%s" \
              "?user=%s&password=%s" \
              "&useUnicode=true" \
              "&characterEncoding=utf8" \
              "&autoReconnect=true" \
              "&failOverReadOnly=false""" \
              % (HOST, PORT, DBNAME, USERNAME, PASSWORD)
        while True:
            cxn = connectionForURI(url)
            sqlhub.processConnection = cxn
            # cxn.debug=True
            try:
                class t_Order(SQLObject):
                    class sqlmeta:
                        formDatabase = True

                    form_title = StringCol(length=200, varchar=True)
                    submit_id = IntCol(length=10)
                    submit_date = TimestampCol()
                    order_id = StringCol(length=200)
                    payment_id = StringCol(length=200)
                    price = DecimalCol(size=10, precision=2)
                    student_id = StringCol(length=20)
                    passwd = StringCol(length=100)
                    c_email = StringCol(length=200)
                break
            except _mysql_exceptions.ProgrammingError, e:
                class t_Order(SQLObject):
                    form_title = StringCol(length=200, varchar=True)
                    submit_id = IntCol()
                    submit_date = TimestampCol()
                    order_id = StringCol(length=200)
                    payment_id = StringCol(length=200)
                    price = DecimalCol(size=10, precision=2)
                    student_id = StringCol(length=20)
                    passwd = StringCol(length=100)
                    c_email = StringCol(length=200)

                break
            except _mysql_exceptions.OperationalError, e:
                logging.error("can't find database")
                # cxn1 = sqlhub.processConnection = connectionForURI(
                #     'mysql://%s:%s/?user=%s&password=%s' % (HOST, PORT, USERNAME, PASSWORD))
                # cxn1.query('CREATE DATABASE %s ' % DBNAME)
                # cxn1.query("GRANT ALL ON %s.* TO '%s'@'%'" % (DBNAME, USERNAME))
                # cxn.close()
        self.order = t_Order
        self.cxn = cxn

    def create(self):
        t_Order = self.order
        t_Order.createTable(ifNotExists=True)

    def insert(self, info):
        if isinstance(info, dict):
            self.order(info)


if __name__ == '__main__':
    info = {u'payment_id': u'2017061721001004380288648858',
            u'form_id': 2,
            u'submit_date': '2017-06-17 01:23:38',
            u'student_id': '132123',
            u'price': 0.01,
            u'order_id': u'IFP-CN101-1706160005691196',
            u'form_title': u'\u533b\u5927\u6559\u52a1\u4e00\u952e\u8bc4\u4ef7',
            u'passwd': '123124',
            u'email': 'still_nighsdft@163.com'}
    order = OrderTable()
    order.create()
    order.insert(info)
