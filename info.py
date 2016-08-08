# -*- coding: utf-8 -*-
# !/usr/bin/python
# Author: Walter Lin
# Crawl personal info from jd.com afte login

import requests
import urllib.request
from bs4 import BeautifulSoup

# def after_login():
# 	#session = requests.session()
# 	info_url = 'http://i.jd.com/user/userinfo/more.html'

# 	# info = session.get(info_url)
# 	# soup = BeautifulSoup(info.text, fromEncoding='GBK')
# 	# title = soup.select('#monthlyIncome')
# 	# print(title)

# 	info_page =  urllib.request.urlopen(info_url)
# 	info = info_page.read()
# 	print(info)

def after_login():
	info_url = 'http://home.jd.com/index.html'        
	info = urllib.request.urlopen(info_url)
	infoSoup = BeautifulSoup(info.text,fromEncoding='GBK')
	print(infoSoup)
