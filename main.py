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
	start_time = timeit.default_timer()

	for i in range(len(username)):
		JD = JDlogin(username[i],password[i])
		JD.login()
		print(timeit.default_timer() - start_time ,'seconds')

		start_time = timeit.default_timer()
		JD.Home()
		print(timeit.default_timer() - start_time , 'seconds')

		# start_time = timeit.default_timer()
		# JD.TotalOrderAmount()
		# print(timeit.default_timer() - start_time , 'seconds')

		# start_time = timeit.default_timer()
		# JD.Address()
		# print(timeit.default_timer() - start_time , 'seconds')
 
