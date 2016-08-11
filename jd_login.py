# -*- coding: utf-8 -*-
# !/usr/bin/python
# Crawl personal info from jd.com afte login

import urllib.request
from bs4 import BeautifulSoup
import re, time, json, requests
from tesseract import image_to_string

class JDlogin(object):
    def __init__(self,un,pw):
        self.headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.82 Safari/537.36',
                        'Accept':'text/javascript, application/javascript, application/ecmascript, application/x-ecmascript, */*; q=0.01',
                        'Accept-Encoding':'gzip, deflate, sdch',
                        'Accept-Language':'zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4',
                        'Connection':'keep-alive',
                        }
        self.session = requests.session()
        self.login_url = 'http://passport.jd.com/uc/login'
        self.post_url = 'http://passport.jd.com/uc/loginService'
        self.auth_url = 'https://passport.jd.com/uc/showAuthCode'
        self.home_url = 'http://home.jd.com'
        self.address_url = 'http://easybuy.jd.com/address/getEasyBuyList.action'
        self.finance_url = 'http://trade.jr.jd.com/async/creditData.action?_dc=1470728844708'
        self.baitiaofen_url = 'http://baitiao.jd.com/v3/ious/score_getScoreInfo'
        self.un = un
        self.pw = pw
        print(un,pw)

    def cookie_login(self):
        '''
            使用登录cookie信息
        '''
        self.session = requests.session()
        self.session.cookies = cookielib.LWPCookieJar(filename='cookies')
        try:
            self.session.cookies.load(ignore_discard=True)
        except:
            print('Cookie 未能加载')

    def get_page(self,url):
        '''
            return soup type object
        '''
        page = self.session.get(url, headers = self.headers)
        soup = BeautifulSoup(page.text,'html.parser')
        return soup

    def get_json(self,url):
        '''return a json file'''
        json_soup = self.get_page(url)
        json_soup = str(json_soup)
        json_data = json.loads(json_soup)
        # print(data)
        return json_data

    def get_authcode(self,url):
        '''
            验证码
        '''
        self.headers['Host'] = 'authcode.jd.com'
        self.headers['Referer'] = 'https://passport.jd.com/uc/login'
        response = self.session.get(url, headers = self.headers)
        with open('authcode.jpg','wb') as f:
            f.write(response.content) 
        authcode = image_to_string('authcode.jpg', False)
        return authcode

    def get_info(self):
        '''
            获取登录相关参数
        '''
        try:
            login_soup = self.get_page(self.login_url)
            input_list = login_soup.select('.form input')

            data = {}
            data['uuid'] = input_list[0]['value']
            data['machineNet'] = ''
            data['machineCpu'] = ''
            data['machineDisk'] = ''
            data['eid'] = input_list[4]['value']
            data['fp'] = 'ca11597ff52d145ba53c3af8b2451fc5' #每一个浏览器都有一个固定的fp(fingerprint)值，由fp.html算出来的
            data['_t'] = input_list[6]['value']
            data['loginType'] = input_list[7]['value']
            rstr = input_list[8]['name']
            data[rstr] = input_list[8]['value']
            acRequired = self.session.post(self.auth_url, data={'loginName':self.un}).text #返回({'verifycode':true})或({'verifycode':false})

            if 'true' in acRequired:
                print ('auth code required ... processing ...')
                acUrl = login_soup.select('.form img')[0]['src2']
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
        '''
            登陆
        '''
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
                
                #登录失败继续重试到成功为止
                if login_page.text != '({"success":"http://www.jd.com"})': 
                    print('LOGIN FAILED', login_page.text )
                else:
                    print(login_page.text)
                    login_test = 1
            except Exception as e:
                print (e)
                pass  

    '''
         完成登录
         ========
        开始抓信息
    '''            

    def get_baitiao(self): 
        '''
            京东理财信息 - 余额、负债、白条分
        '''
        print('creditData: ', self.get_json(self.finance_url)) #理财信息
        print('totalDebt: ', self.get_json(self.finance_url)['totalDebt']) #负债
        print('baitiao_fen: ', self.get_page(self.baitiaofen_url)) #白条分


 
    def get_order(self,year,page):
        '''
            抓取一年的订单信息
        '''
        order_url = 'http://order.jd.com/center/list.action?search=0&d=' + year + '&s=4096&page=' + page
        
        order_soup = self.get_page(order_url)
        amounts = order_soup.find_all('div',  {'class':'amount'})
        amount_list = []
        for amount in amounts: 
            sale = re.findall("\d+\.\d+",amount.text)
            amount_list.append(sale[0])
        amount_list = [float(i) for i in amount_list]
        total_amount = sum(amount_list)
        print('This user spent ', total_amount, 'rmb in ', year, 'in page ', page)
        return total_amount


        # order_url = 'http://order.jd.com/lazy/getOrderProductInfo.action'
        # lazy_page = self.session.get(order_url, headers = self.headers)
        # lazy_soup = BeautifulSoup(lazy_page.text,'html.parser')
        # print(lazy_soup)
    
    def get_totalOrderAmount(self):
        '''
            loop over Order
            1 is for recent three months
            2 is for this year
            3 is for before 2013
        '''
        all_year_amount = []
        pages = {'1','2'}
        years = {'1','2','3','2015','2014','2013'} 
        
        for year in years:
            for page in pages:
                all_year_amount.append(self.get_order(year, page))
        all_year_amount = sum(all_year_amount)
        print('This user totally spent', all_year_amount, ' rmb on jd.com')

    def get_address(self):
        '''
            抓取收货地址信息
        '''
        address_soup = self.get_page(self.address_url)
        addresses = address_soup.find_all('div',  {'class':'fl'})
        address_list = []
        for address in addresses:
            address_list.append(re.sub(r'\W','',address.text))
        print(address_list)