# -*- coding: utf-8 -*- 
"""

"""
#   @Time:  2017/6/23 1:00
#   @Author:still_night@163.com
#   @File:  JwUser.py
from __future__ import unicode_literals

import const
import requests
from bs4 import BeautifulSoup
from threadpool import makeRequests,ThreadPool
# from multiprocessing.dummy import Pool as MultiPool
import json
import time
import random
from log import logging


class JwglUser():
    '''教务系统的用户类'''

    def __init__(self, user_id=None, passwd=None):
        # self.user_id=user_id
        # self.passwd=passwd
        self.set_user(user_id, passwd)
        self.req = requests.session()
        self.req.headers = const.headers.copy()
        self.login_status = False

    def set_user(self, user_id, passwd=None):
        '''设置用户名和密码'''
        if isinstance(user_id, int):
            user_id = str(user_id)

        self.user_id = user_id
        self.passwd = passwd
        self.default_params = {
            'gnmkdmKey': 'index',
            'sessionUserKey': self.user_id
        }

    def is_password_valid(self):
        passwd_valid=False
        retry=3
        while retry>0:
            retry-=1
            try:
                value=self.check_user_passwd()
            except const.LoginError:
                passwd_valid = False
                break
            except:
                pass
            else:
                if value==const.NoError:
                    passwd_valid=True
                    break
            finally:
                self.req.close()
        else:
            raise const.NetworkError
        return passwd_valid

    def check_user_passwd(self,user_id=None,passwd=None):
        '''登陆检查,用户名和密码是否正确'''

        data = {
            'yhm': self.user_id,
            'mm': self.passwd,
            'yzm': ''
        }
        if user_id:
            data['yhm']=user_id
        if passwd:
            data['mm']=passwd

        try:
            resp = self.req.post(const.login_check_page, data=data)
        except requests.ConnectionError:

            raise const.NetworkError
        else:
            if resp.text.find('"status":"success"') == -1:
                logging.error("%s %s %s" %(data['yhm'], data['mm'], resp.text))
                raise const.LoginError
            else:
                return const.NoError

    def login(self):
        '''登陆,获取cookie'''
        if not self.user_id:
            logging.error('invalid user id')
            raise const.LoginError
        if not self.passwd:
            logging.error('invalid user passwd')
            raise const.LoginError
        try:
            self.check_user_passwd()
        except (const.NetworkError,const.LoginError):
            raise const.LoginError
        post_data = {
            'yhm': self.user_id,
            'mm': self.passwd,
            'yzm': ''
        }
        try:
            self.req.post(const.login_page, data=post_data)
        except KeyboardInterrupt:
            raise
        except Exception as e:
            logging.error('login error %s '% e.message)
            raise const.LoginError
        else:
            if self.is_login():
                self.login_status = True
                return const.NoError
            else:
                raise const.LoginError

    def change_password(self, new_password):
        if not isinstance(new_password, str):
            raise TypeError

        if self.is_login() == False:
            self.login()
        params = self.default_params.copy()
        data = {
            'doType': 'save',
            'ymm': self.passwd,
            'mm': new_password,
            'yhmmdj': '2',
            'nmm': new_password
        }
        response = self.req.post(const.change_password_page, params=params, data=data)
        if response.text.find('修改成功') != -1:
            self.set_user(self.user_id, new_password)
            self.login()
            return const.NoError
        else:
            raise const.ChangePasswordError

    def is_login(self):
        '''获取该学生的登录信息来判断是否成功登陆'''
        # http://202.118.40.67/jwglxt/xtgl/index_cxYhxxIndex.html?xt=jw&gnmkdmKey=index&sessionUserKey=1471112
        params = {
            u'xt': u'jw',
            u'gnmkdmKey': u'index',
            u'sessionUserKey': self.user_id
        }
        response = self.req.get(const.user_info_page, params=params)
        if response.text.find(u'<title>登录超时</title>') == -1:
            self.login_status = True
            return True
        else:
            self.login_status = False
            return False

    def pj_all_teacher(self):
        '''评价所有老师'''
        if not self.is_login():
            self.login()
        all_teacher_info = self.get_pj_index()

        def __pj_act(each_teacher):  # 用到了多线程的Pool.map  这是执行的动作
            if each_teacher['status'] != u'提交':
                logging.debug("%s:%s %s"%(self.user_id,each_teacher['teacher_name'], each_teacher['kc_name']))
                while not self.send_submit_pj(each_teacher):
                    logging.error( "%s %s %s"%(each_teacher['teacher_name'], each_teacher['kc_name'], u'重试'))

        # 多线程处理
        # pool = MultiPool()
        # pool.map(__pj_act, all_teacher_info)
        pool=ThreadPool(8)
        pj_reqs=makeRequests(__pj_act,all_teacher_info)
        [pool.putRequest(req) for req in pj_reqs]
        pool.wait()

        # for each in all_teacher_info:
        #     __pj_act(each)
        # for each_teacher in all_teacher_info:
        #     if each_teacher['status']!='提交':
        #         print(each_teacher['teacher_name'],each_teacher['kc_name'])
        #         while not self.send_save_pj(each_teacher):
        #             print(each_teacher['teacher_name'], each_teacher['kc_name'],'重试')

    def get_pj_index(self):
        '''获取学生的所有老师的列表'''
        para = {'gnmkdmKey': const.pj_gnkey, 'sessionUserKey': self.user_id}
        datas = {'gnmkdm': const.pj_gnkey, 'czdmKey': '00'}
        pj_index_page = self.req.post(r'http://202.118.40.67/jwglxt/xspjgl/xspj_cxXspjIndex.html', params=para,
                                      data=datas)
        soup = BeautifulSoup(pj_index_page.text, 'html.parser')
        # print(pj_index_page.text)
        pj_list = []
        for each in soup.select('#jxb_body tr'):
            info = {
                'data-kch_id': each['data-kch_id'],
                'data-jgh_id': each['data-jgh_id'],
                'data-xsdm': each['data-xsdm'],
                'data-jxb_id': each['data-jxb_id'],
                'status': each.select_one('td:nth-of-type(1) > span').text,
                'kc_name': each.select_one('td:nth-of-type(2) ').text.strip(),
                'xsdm_name': each.select_one('td:nth-of-type(3) ').text.strip(),
                'teacher_name': each.select_one('td:nth-of-type(4) ').text.strip()
            }
            pj_list.append(info)
        return pj_list

    def get_pj_subpage(self, info):
        '''获取对某教师评价的详细页面'''
        data = {
            'jxb_id': info['data-jxb_id'],
            'kch_id': info['data-kch_id'],
            'xsdm': info['data-xsdm'],
            'jgh_id': info['data-jgh_id']
        }
        params = {
            'gnmkdmKey': const.pj_gnkey,
            'sessionUserKey': self.user_id
        }
        pj_subpage = self.req.post(const.pj_detail_page, params=params, data=data)
        return pj_subpage

    def send_save_pj(self, info):
        '''生成并保存评价'''
        params = {
            'gnmkdmKey': const.pj_gnkey,
            'sessionUserKey': self.user_id
        }
        subpage = self.get_pj_subpage(info)
        postform = self.get_pj_post_form(subpage)
        postform['tjzt'] = '0'  # 表示提交:1 保存:0
        response = self.req.post(const.pj_save_page, params=params, data=postform)
        # print(response.text)
        if response.text == u'"评价保存成功！"':
            return True
        else:
            return False

    def send_submit_pj(self, info):
        '''生成并提交评价'''
        params = {
            'gnmkdmKey': const.pj_gnkey,
            'sessionUserKey': self.user_id
        }
        subpage = self.get_pj_subpage(info)
        postform = self.get_pj_post_form(subpage)
        postform['tjzt'] = '1'  # 表示提交:1 保存:0
        response = self.req.post(const.pj_submit_page, params=params, data=postform)
        # print(response.text)
        if response.text == u'"评价提交成功！"':
            return True
        else:
            return False

    def get_pj_post_form(self, subpage):
        '''获取对该老师评价页面应该post 的数据 '''
        soup = BeautifulSoup(subpage.text, 'html.parser')
        postform = {}
        pj_body = soup.select_one('.panel-body.xspj-body')
        for each in pj_body.attrs:
            if each.find('data-') == 0 and pj_body[each]:
                postform[each.lstrip('data-')] = pj_body[each]

        for each_pjdx_index, each_pjdx in enumerate(pj_body.select('.panel.panel-default.panel-pjdx')):
            modelstr = "modelList[{}].".format(each_pjdx_index)
            postform[modelstr + 'pjmbmcb_id'] = each_pjdx['data-pjmbmcb_id']
            postform[modelstr + 'pjdxdm'] = each_pjdx['data-pjdxdm']
            # postform[modelstr + 'py'] = each_pjdx.select_one('#{}_py'.format(each_pjdx['data-pjmbmcb_id'])).text
            postform[modelstr + 'py'] = ''
            postform[modelstr + 'xspfb_id'] = each_pjdx['data-xspfb_id']
            for each_xspj_index, each_xspj in enumerate(each_pjdx.select('table.table-xspj')):
                xspj_str = modelstr + 'xspjList[{}].'.format(each_xspj_index)
                postform[xspj_str + 'pjzbxm_id'] = each_xspj['data-pjzbxm_id']
                for each_child_xspj_index, each_child_xspj in enumerate(each_xspj.select('tr.tr-xspj')):
                    child_xspj_str = xspj_str + 'childXspjList[{}].'.format(each_child_xspj_index)
                    postform[child_xspj_str + 'pfdjdmxmb_id'] = each_child_xspj.select('input.radio-pjf')[0][
                        'data-pfdjdmxmb_id']
                    postform[child_xspj_str + 'pjzbxm_id'] = each_child_xspj['data-pjzbxm_id']
                    postform[child_xspj_str + 'pfdjdmb_id'] = each_child_xspj['data-pfdjdmb_id']
                    postform[child_xspj_str + 'zsmbmcb_id'] = each_child_xspj['data-zsmbmcb_id']

        return postform

filelock=[False]
def writefile(text,filename='all_xs_detail.json',sep='\n'):
    while filelock[0] == True:
        time.sleep(random.randint(1, 100) / 1000)
    filelock[0] = True
    with open(filename, 'a',encoding='utf-8') as fp:
        fp.write(text )
        fp.write(sep)
        fp.close()
    filelock[0] = False



def main():
    stu1=JwglUser("1","2")
    try:
        stu1.check_user_passwd()
    except const.LoginError:
        print ("password Wrong")
    else:
        print ("password true")
        stu1.pj_all_teacher()

    # t1 = JwglTeacher(jgh, jgmm)
    # t1.login()
    # all_detail=t1.get_all_jxb_xs_list()


    # stu1 = Jwgl_user(stu_info[0], stu_info[1])
    # adict=stu1.get_pj_post_form(subpage)
    # for key in sorted(adict.keys()):
    #     print(key+':'+adict[key])
    # stu1.login()
    # stu1.pj_all_teacher()
    # print(stu1.req.cookies)
    # infos=stu1.get_pj_index()
    # print(infos)
    # info1=infos[32]
    # print(stu1.send_save_pj(info1))
    # print(stu1.get_pj_subpage(info1).text)
    # subpage=stu1.get_pj_subpage(info1)
    # print(subpage.text)
    # # stu1.get_pj_subpage(info1).text
    'http://202.118.40.67/jwglxt/xsxkjk/xsxkcx_cxJxbxsList.html?doType=query&gnmkdmKey=N255005&sessionUserKey=20101175'


if __name__ == "__main__":
    main()
