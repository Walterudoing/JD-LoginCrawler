# -*- coding: utf-8 -*-
# !/usr/bin/python
# Author: Walter Lin
# Crawl personal info from jd.com afte login

import requests
import urllib.request
from bs4 import BeautifulSoup
import time
import re

class JDlogin(object):
    def __init__(self,un,pw):
        self.headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.82 Safari/537.36',
                        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                        'Accept-Encoding':'gzip, deflate, sdch',
                        'Accept-Language':'zh-CN,zh;q=0.8',
                        'Connection':'keep-alive',
                        }
        self.session = requests.session()
        self.login_url = 'http://passport.jd.com/uc/login'
        self.post_url = 'http://passport.jd.com/uc/loginService'
        self.auth_url = 'https://passport.jd.com/uc/showAuthCode'
        self.home_url = 'http://home.jd.com/'
        self.address_url = 'http://easybuy.jd.com/address/getEasyBuyList.action'
        self.un = un
        self.pw = pw
        print(un,pw)

    def cookie_login(self):
        '''使用登录cookie信息'''
        self.session = requests.session()
        self.session.cookies = cookielib.LWPCookieJar(filename='cookies')
        try:
            self.session.cookies.load(ignore_discard=True)
        except:
            print('Cookie 未能加载')

    def get_authcode(self,url):
        '''验证码'''
        self.headers['Host'] = 'authcode.jd.com'
        self.headers['Referer'] = 'https://passport.jd.com/uc/login'
        response = self.session.get(url, headers = self.headers)
        with open('authcode.jpg','wb') as f:
            f.write(response.content) 
        authcode = input('plz enter authcode:')
        return authcode

    def get_info(self):
        '''获取登录相关参数'''
        try:
            page = self.session.get(self.login_url, headers = self.headers )
            soup = BeautifulSoup(page.text,'html.parser')
            input_list = soup.select('.form input')

            data = {}
            data['uuid'] = input_list[0]['value']
            data['machineNet'] = ''
            data['machineCpu'] = ''
            data['machineDisk'] = ''
            data['eid'] = input_list[4]['value']
            data['fp'] = 'ca11597ff52d145ba53c3af8b2451fc5' #每一台机器都有一个固定的fp(fingerprint)值，具体怎么算的不清楚
            data['_t'] = input_list[6]['value']
            data['loginType'] = input_list[7]['value']
            rstr = input_list[8]['name']
            data[rstr] = input_list[8]['value']
            acRequired = self.session.post(self.auth_url, data={'loginName':self.un}).text #返回({'verifycode':true})或({'verifycode':false})

            if 'true' in acRequired:
                print ('need authcode, plz find it and fill in ')
                acUrl = soup.select('.form img')[0]['src2']
                acUrl = 'http:{}&yys={}'.format(acUrl,str(int(time.time()*1000)))
                authcode = self.get_authcode(acUrl)
                data['authcode'] = authcode
            else:
                data['authcode'] = ''
        except Exception as e:
            print (e)
        finally:
            return data

    def login(self):
        '''登陆'''
        login_test = None
        while login_test is None:
            postdata = self.get_info()
            postdata['loginname'] = self.un
            postdata['nloginpwd'] = self.pw
            postdata['loginpwd'] = self.pw

            try:
                self.headers['Host'] = 'passport.jd.com'
                self.headers['Origin'] = 'https://passport.jd.com'
                self.headers['X-Requested-With'] = 'XMLHttpRequest'
                login_page = self.session.post(self.post_url, data = postdata, headers = self.headers) 
                
                #登录重试
                if login_page.text != '({"success":"http://www.jd.com"})': 
                    print('LOGIN FAILED',login_page.text )
                else:
                    print(login_page.text)
                    login_test = 1
            except Exception as e:
                print (e)
                pass

    def Home(self):
        '''抓取个人主页的信息'''
        '''余额、白条、实名认证'''
        home_page = self.session.get(self.home_url, headers = self.headers)
        home_soup = BeautifulSoup(home_page.text,'html.parser')
        #余额
        a_s = home_soup.find_all('a', {'id':'BalanceCount'})
        for a in a_s:
            a_label = a.previousSibling.previousSibling.text
            print(a_label, a.text)

        
        #京东豆
        b_s = home_soup.find_all('a', {'id':'JingdouCount'})
        for b in b_s:
            b_label = b.previousSibling.previousSibling.text
            print(b_label, a.text)

        
        # #白条
        # baitiao_list = []
        # baitiaos = home_soup.find_all('div', {'class':'baitiao-info'})
        # for baitiao in baitiaos:
        #     baitiao_list.append(re.sub(r'\W','',baitiao.text))
        # print(baitiao_list)
        # #实名认证 real name auth (rna)
        # rna_list = []
        # rnas = home_soup.find_all('div', {'class':'acco-item'})
        # for rna in rnas:
        #     rna_list.append(re.sub(r'\W','',rna.text))
        # print(rna_list)

        # #fore1
        # fore1_list = []
        # fore1s = home_soup.find_all('li', {'class':'fore1'})
        # for fore1 in fore1s:
        #     fore1_list.append(re.sub(r'\W','',fore1.text))
        # print(fore1)

        
    def Order(self,year,page):
        '''抓取一年的订单信息'''
        year_url = 'http://order.jd.com/center/list.action?search=0&d=' + year + '&s=4096&page=' + page
        order_page = self.session.get(year_url, headers = self.headers)
        order_soup = BeautifulSoup(order_page.text,'html.parser')
        amounts = order_soup.find_all('div',  {'class':'amount'})
        amount_list = []
        for amount in amounts: 
            sale = re.findall("\d+\.\d+",amount.text)
            amount_list.append(sale[0])
        amount_list = [float(i) for i in amount_list]
        total_amount = sum(amount_list)
        print('This user spent ', total_amount, ' rmb in ', year, 'in page ', page)
        return total_amount


        order_url = 'http://order.jd.com/lazy/getOrderProductInfo.action'
        lazy_page = self.session.get(order_url, headers = self.headers)
        lazy_soup = BeautifulSoup(lazy_page.text,'html.parser')
        print(lazy_soup)
    
    def TotalOrderAmount(self):
        '''loop over Order'''
        all_year_amount = []
        pages = {'1','2'}
        years = {'1','2','3','2015','2014','2013'} 
        # 1 is for recent three months
        # 2 is for this year
        # 3 is for before 2013
        for year in years:
            for page in pages:
                all_year_amount.append(self.Order(year, page))
        all_year_amount = sum(all_year_amount)
        print('This user totally spent', all_year_amount, ' rmb on jd.com')

    def Address(self):
        '''抓取收货地址信息'''
        address_page = self.session.get(self.address_url, headers = self.headers)
        address_soup = BeautifulSoup(address_page.text,'html.parser')
        addresses = address_soup.find_all('div',  {'class':'fl'})
        address_list = []
        for address in addresses:
            address_list.append(re.sub(r'\W','',address.text))
        print(address_list)