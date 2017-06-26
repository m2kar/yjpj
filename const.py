# -*- coding: utf-8 -*-
"""
变量类 其中mail setting 必须更改
@File:  const.py
@Author: still_night
@Contact:still_night@163.com
@Date: 2017/2/25
@Time: 11:46
@License: GPL
"""
import sys, os
# sys.path.append("site-packages")
if not sys.platform == 'win32' and os.path.exists("/home/bae"):
    sys.path.append('/home/bae/app/deps')

# mail setting
# todo 设置下面为你自己的
IMAPHOST = 'imap.sina.com'
IMAPUSERNAME = "imap_user"
IMAPPASSWORD = "imap_password"
PAYMENT_DIR = "yjpj_payment"
WORKORDER_DIR = "work_order"

SMTPFULLADDRESS = "smtp_useraddress"
SMTPHOST = "smtp_host"
SMTPUSERNAME = "smtp_username"
SMTPPASSWORD = "smtp_password"

if not sys.platform == 'win32' and os.path.exists("/home/bae"):
    LOGFILE = "/home/bae/log/jwpj.log"
    INFOLOGFILE = "/home/bae/log/jwpj_info.log"
    ERRLOGFILE = "/home/bae/log/jwpj_err.log"
else:
    LOGFILE = "./jwpj.log"
    INFOLOGFILE = "./jwpj_info.log"
    ERRLOGFILE = "./jwpj_err.log"
# '''一些常量'''
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko)'
                  ' Chrome/55.0.2883.87 Safari/537.36'

}
'''下面是一些链接'''
main_url = r'http://202.118.40.67/jwglxt/'  # 教务系统的根目录
login_page = main_url + 'xtgl/login_login.html'  # 登陆页面
login_check_page = main_url + 'xtgl/login_cxCheckYh.html'  # 登陆检查
change_password_page = main_url + 'xtgl/mmgl_xgMm.html'  # change password
user_info_page = main_url + 'xtgl/index_cxYhxxIndex.html'  # 用户信息
pj_index_url = main_url + 'xtgl/xspj_cxXspjIndex.html'  # 评价教师列表
pj_detail_page = main_url + 'xspjgl/xspj_cxXspjDisplay.html'  # 评价的详情页
pj_save_page = main_url + 'xspjgl/xspj_bcXspj.html'  # 保存评价的posturl
pj_submit_page = main_url + 'xspjgl/xspj_tjXspj.html'  # 提交评价的posturl
# pj_subpage='http://202.118.40.67/jwglxt/xspjgl/xspj_cxXspjDisplay.html'
pj_gnkey = 'N4010'  # 评价的功能号

get_kcb_index_page = main_url + 'kbdy/jskbdy_cxJskbdyList.html'
get_kcb_detail_page = main_url + 'kbdy/jskbdy_cxJsKb.htm'

from socket import error as SocketError

class LoginError(BaseException):
    '''登陆错误'''
    pass


class NetworkError(BaseException):
    pass


class JsonError(BaseException):
    pass


class ChangePasswordError(BaseException):
    pass


NoError = None
