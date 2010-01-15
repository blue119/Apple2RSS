#!/usr/bin/python
# -*- coding: utf8 -*-

#v0.1 can be run but not is good.
#v0.2 patch to support new format

from urllib import urlopen
from BeautifulSoup import BeautifulSoup
from time import gmtime, strftime, sleep
import sys, re, copy
import urllib2

reload(sys)
sys.setdefaultencoding('utf8')

class apple_news_api():
	"""
the api originally is my private using to grabe news from nextmedia web side. then, convert to RSS format and exclude 
every ad.  
	"""
	def __init__(self):
		self.news_contents = []
		self.news_items = {}
		self.news_chunks = {}
		self.home_url = 'http://tw.nextmedia.com/'
		#self.catalog_page = unicode(AppleNewHome, 'big5', 'ignore')
		self.catalog_page = urlopen( self.home_url + 'applenews/todayapple').read()
		self.catalog_page = BeautifulSoup(self.catalog_page)

	def get_list(self):
		"""
<div id="nl_box"> <- Title Item
<span class="nl_unit_bar_title">頭條要聞</span> <- Classify
<span class="nl_unit_second_title">頭條</span> <-  subClassify
<div id="nl_unitlist"> <= subClassify link
		"""
		ClassifySector = self.catalog_page.findAll('div', {'id':'nl_box'})
		for i in ClassifySector:
			self.counting = 0
			ClassifyName = i.find('span', {'class':'nl_unit_bar_title'}).string
			print ClassifyName

			for j in i.findAll('span', {'class':'nl_unit_second_title'}):
				subClassifyName = j.string
				#print subClassifyName

				for k in i.findAll('div', {'id':'nl_unitlist'})[self.counting].findAll('a'):
					print '[%s] %s : %s' %(subClassifyName, k.string, k['href']) 
					self.news_items['subClassify'] = str(subClassifyName)
					self.news_items['title'] = str(k.string)
					self.news_items['href'] = str(k['href'])
					self.news_contents.append(copy.copy(self.news_items))

				self.news_chunks[ClassifyName] = copy.copy(self.news_contents)
				self.counting += 1
				Contents = []




