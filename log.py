# -*- coding: utf-8 -*- 
"""

"""
#   @Time:  2017/6/23 8:23
#   @Author:still_night@163.com
#   @File:  log.py

import logging
import const
logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                filename=const.LOGFILE,
                filemode='w')

#################################################################################################
#定义一个StreamHandler，将INFO级别或更高的日志信息打印到标准错误，并将其添加到当前的日志处理对象#
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

errlog=logging.FileHandler(const.ERRLOGFILE)
errlog.setLevel(logging.WARNING)
errformatter=logging.Formatter('%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s')
errlog.setFormatter(errformatter)
logging.getLogger('').addHandler(errlog)
