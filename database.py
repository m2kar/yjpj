#! python3
#coding=utf-8
"""

@File:  database.py
@Author: still_night
@Contact:still_night@163.com
@Date: 2017/2/25
@Time: 13:45
@License: GPL
"""

import os
from sqlalchemy import *

from . import const

global_table_list=(
    ('t_proxies',(
        Column('c_ip',String(20)),
        Column('c_port',String(5)),
        Column('c_location',String(30)),
        Column('c_type',String(10)),
        Column('c_speed',DECIMAL(6,3)),
        Column('c_delay',DECIMAL(6,3)),
        Column('c_life',TIMESTAMP)
    ))
)

def connect_database():
    global DATABASE_CONNECTION
    isexists=os.path.isfile(const.database_filename)
    conn=sqlite3.connect(const.database_filename)





def main():
    pass


if __name__ == '__main__':
    main()