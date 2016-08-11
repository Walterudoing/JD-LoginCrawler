# -*- coding: utf-8 -*-
# !/usr/bin/python
# Author: Walter Lin
# Crawl personal info from jd.com afte login

import requests
from bs4 import BeautifulSoup
from jd_login import JDlogin
import timeit


username = ['USERNAME']
password = ['PASSWORD']


if __name__=='__main__':
	all_time = timeit.default_timer()

	for i in range(len(username)):
		start_time = timeit.default_timer()
		JD = JDlogin(username[i],password[i])
		JD.login()
		print(timeit.default_timer() - start_time ,'seconds')

		start_time = timeit.default_timer()
		JD.get_baitiao()
		print(timeit.default_timer() - start_time , 'seconds')

		# start_time = timeit.default_timer()
		# JD.realname_auth()
		# print(timeit.default_timer() - start_time , 'seconds')

		start_time = timeit.default_timer()
		JD.get_totalOrderAmount()
		print(timeit.default_timer() - start_time , 'seconds')

		start_time = timeit.default_timer()
		JD.get_address()
		print(timeit.default_timer() - start_time , 'seconds')
		
	print('totally spent ',timeit.default_timer() - all_time , 'seconds')