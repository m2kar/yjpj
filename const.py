#! python3
# coding=utf-8
"""

@File:  const.py
@Author: still_night
@Contact:still_night@163.com
@Date: 2017/2/25
@Time: 11:46
@License: GPL
"""
import sys
#databse
database_filename='database.db'


server_url = r'http://www.xicidaili.com/nn'
page_counts = 10
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/56.0.2924.87 Safari/537.36'
}

#mail setting
IMAPHOST= 'imap.sina.com'
SMTPHOST="smtp.sina.com"
MAILUSERNAME= "yjpj_service"
MAILPASSWORD= "rzq123"

if sys.platform == 'win32':
    LOGFILE="./jwpj.log"
    ERRLOGFILE="./jwpj_err.log"
else:
    LOGFILE="/home/bae/log/jwpj.log"
    LOGFILE = "/home/bae/log/jwpj_err.log"