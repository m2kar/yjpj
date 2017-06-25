# -*- coding: utf-8 -*- 
"""

"""
#   @Time:  2017/6/23 1:00
#   @Author:still_night@163.com
#   @File:  JwUser.py
from __future__ import unicode_literals

import requests
from bs4 import BeautifulSoup
from multiprocessing.dummy import Pool as MultiPool
import json
import time
import random
from log import logging
class const():
    '''一些常量'''
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
    get_kcb_detail_page=main_url+'kbdy/jskbdy_cxJsKb.htm'

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
                logging.error("%s %s %s" %(data['yhm'], data['mm'], resp.text.decode()))
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
        pool = MultiPool()
        pool.map(__pj_act, all_teacher_info)
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


class JwglTeacher(JwglUser):
    def get_all_kcb_index(self, curent_page=1, show_count=99999):
        params = self.default_params.copy()
        params['gnmkdmKey'] = 'N214510'
        data = {'_search': 'false',
                'jg_id': '',
                'jgh': '',
                'nd': '1487260366538',
                'queryModel.currentPage': str(curent_page),
                'queryModel.showCount': str(show_count),  # 设为最大
                'queryModel.sortName': 'jgh',
                'queryModel.sortOrder': 'asc',
                'time': '15',
                'xnm': '2016',
                'xqh_id': '',
                'xqm': '3',
                'zcmc': ''}
        response = self.req.post(const.get_kcb_index_page, params=params, data=data)
        return json.loads(response.text)

    def get_kcb_detail(self, info):
        params = self.default_params.copy()
        params['gnmkdmKey'] = 'N214510'
        data = {'jgh': info['jgh'],
                'jgh_id': info['jgh_id'],
                'jgmc': '',
                'xm': info['xm'],
                'xnm': info['xnm'],
                'xnmc': info['xnmc'],
                'xqh_id': info['xqh_id'],
                'xqm': info['xqm'],
                'xqmmc': info['xqmmc']
                }
        try:
            # response=self.req.post(const.get_kcb_detail_page,params=params,data=data)
            response=self.req.post('http://202.118.40.67/jwglxt/kbdy/jskbdy_cxJsKb.html?gnmkdmKey=N214510&sessionUserKey=20101175',data=data)
            if response.status_code==404:
                raise const.NetworkError
        except KeyboardInterrupt:
            raise
        except Exception as e :
            logging.error('get_kcb_detail:request post %s'%e.message)
            raise const.NetworkError

        try:
            retval = json.loads(response.text)
        except KeyboardInterrupt:
            raise
        except Exception as e:
            logging.error(' get_kcb_detail:json %s'%e.message)
            raise const.JsonError
        return retval

    def __act_all_kcb_detail(self,info):
        trycount = 3
        while trycount > 0:
            time.sleep(random.randint(0, 100) / 1000)
            try:
                each_detail = self.get_kcb_detail(info)
            except (const.NetworkError, const.JsonError) as e:
                logging.error("%s %s" %(e, info['jgh']))
                trycount -= 1
            else:
                print(each_detail['kbList'])
                writefile(str(each_detail['kbList'])[1:-1],sep=',\n')
                break


    def get_all_kcb_detail(self):
        # all=self.get_all_kcb_index()
        all=json.load(open('all_teacher_2016.json',encoding='utf-8'))
        # all_detail=json.loads('{}')
        # all_detail['items']=[]
        writefile("{'items':[")
        pool=MultiPool(5)
        pool.map(self.__act_all_kcb_detail,all['items'])
        writefile("]}")
        # for info in all['items']:
        # all_detail['count']=len(all_detail['items'])
        return const.NoError


    def __act_all_jxb_xs_list(self,info):
        trycount = 3
        while trycount > 0:
            time.sleep(random.randint(0, 100) / 1000)
            try:
                each_jxb_xs_list = self.get_jxb_xs_list(info['jxb_id'])
            except (const.NetworkError, const.JsonError) as e:
                print(e, info['jxbzc'])
                trycount -= 1
            else:
                print(each_jxb_xs_list)
                writefile("'%s' : %s" %( info['jxb_id'],str(each_jxb_xs_list)),sep=',\n')
                break

    # def get_all_jxb_xs_list(self):
    #     # all=self.get_all_kcb_index()
    #     # all=json.load(open('all_teacher_2016.json',encoding='utf-8'))
    #     from  cmujw2.all_jxb import all_jxb_list
    #     # all_detail=json.loads('{}')
    #     # all_detail['items']=[]
    #     writefile("{")
    #     pool=MultiPool(5)
    #     pool.map(self.__act_all_jxb_xs_list,all_jxb_list)
    #     writefile("}")
    #     # for info in all['items']:
    #     # all_detail['count']=len(all_detail['items'])
    #     return const.NoError


    def get_jxb_xs_list(self,jxb_id,xnm='2016',xqm='3'):
        xcb_page = 'http://202.118.40.67/jwglxt/xsxkjk/xsxkcx_cxJxbxsList.html?' \
                   'doType=query&gnmkdmKey=N255005&sessionUserKey=20101175'
        params={
            'doType':'query',
            'gnmkdmKey':'N255005',
            'sessionUserKey':'20101175'
        }
        data={'_search': 'false',
         # 'jxb_id': '3CC54FBDEE80B3C2E05342C7A8C0534E',
         'jxb_id': jxb_id,
         'nd': '1487309019364',
         'queryModel.currentPage': '1',
         'queryModel.showCount': '100000',
         'queryModel.sortName': 'xh desc,bj,xm',
         'queryModel.sortOrder': 'asc',
         'time': '1',
         'xnm': xnm,
         'xqm': xqm}
        try:
            response=self.req.post(xcb_page,data=data)
            if response.status_code==404:
                raise const.NetworkError
        except KeyboardInterrupt:
            raise
        except Exception as e:
            raise const.NetworkError
        else:
            try:
                retval=json.loads(response.text)
            except KeyboardInterrupt:
                raise
            except Exception as e :
                raise const.JsonError
            else:
                return retval

    def get_person_info(self):
        info_page=const.main_url + 'jsxx/jsgrxx_cxJsgrxx.html'
        gnKey='N1585'
        params={
            '_t':'1487314394930',
            'gnmkdmKey': gnKey,
            'sessionUserKey':self.user_id
        }
        data={
            'gnmkdm':gnKey,
            'czdmKey':'00'
        }
        try:
            response=self.req.post(info_page,params=params,data=data)
            if response.status_code==404:
                raise const.NetworkError
        except KeyboardInterrupt:
            raise
        except Exception as e:
            raise const.NetworkError
        else:
            return response.text


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
    stu1=JwglUser("1452110","sw19961003seven")
    try:
        stu1.check_user_passwd()
    except const.LoginError:
        print ("password Wrong")
    else:
        print ("password true")
        stu1.pj_all_teacher()
    # stu_info = ('1471112', 'a643926926')
    # jgh='19991070'
    # jgmm='qwerty123456'
    # t1 = JwglTeacher(jgh, jgmm)
    # t1.login()
    # all_detail=t1.get_all_jxb_xs_list()

    # stu1=Jwgl_user('132601','rzq123')
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
