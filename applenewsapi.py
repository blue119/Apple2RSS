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
		self.news_list = {}
		self.home_url = 'http://tw.nextmedia.com/'
		#self.catalog_page = unicode(AppleNewHome, 'big5', 'ignore')
		self.catalog_page = urlopen( self.home_url + 'applenews/todayapple').read()
		self.catalog_page = BeautifulSoup(self.catalog_page)

	def get_title(self, PageContent):
		p = re.compile('^<title>(.*)\ \|\ .*\ \|\ .*\ \|.*\|.*</title>')
		Title = p.findall(str(PageContent.title).replace('\n', ''))
		try:
			return Title[0]
		except IndexError:
			print 'Can not parsing this title : "' + str(PageContent.title) + '"'
			Title = None
			return Title

	def get_list(self, DEBUG = False):
		"""
<div id="nl_box"> <- Title Item
<span class="nl_unit_bar_title">頭條要聞</span> <- Classify
<span class="nl_unit_second_title">頭條</span> <-  subClassify
<div id="nl_unitlist"> <= subClassify link
		"""
		news_items = {}
		news_contents = []
		ClassifySector = self.catalog_page.findAll('div', {'id':'nl_box'})
		for i in ClassifySector:
			counting = 0
			classify_by_name = i.find('span', {'class':'nl_unit_bar_title'}).string
			if DEBUG:
				print '<<<' + classify_by_name + '>>>'

			for j in i.findAll('span', {'class':'nl_unit_second_title'}):
				sub_classify_by_name = j.string
				#print classify_by_name

				for k in i.findAll('div', {'id':'nl_unitlist'})[counting].findAll('a'):
					if DEBUG:
						print '[%s] %s : %s' %(sub_classify_by_name, k.string, k['href']) 
					news_items['subClassify'] = str(sub_classify_by_name)
					news_items['title'] = str(k.string)
					news_items['href'] = str(k['href'])
					news_contents.append(copy.copy(news_items))
				counting += 1
			self.news_list[classify_by_name] = copy.copy(news_contents)
			news_contents = []

		
	def page_parser(self, content, DEBUG=False):
		"""
		"""
		summary = []
		summary.append(self.get_title(content))
		if DEBUG:
			print('Title: %s' %summary[0])

		page_content = content.find('div', {'id':'article_left'})

		# some page have no tag for page_content
		if page_content is None:
			page_content = content

		try:
			img = str(page_content.find('script', {'language':'javascript'}))
			p = re.compile('g_ImageTable.*\"(.*)\",\ \"(.*)\",.*javascript:.*\(\'(.*)\',\'http.*\',\'.*\',\'.*\)\"\)')
			result = p.findall(img)
			SmallIMG, BigIMG, titleIMG = result[0]
			summary.append([SmallIMG, BigIMG, titleIMG])
		except AttributeError: #No Picture in intro
			pass

		#Grab alticl section
		p = re.compile('.*iclickAdBody_Start\"\>\<\/span\>(.*)\<span\ name\=\"iclickAdBody_End\"\ id\=.*')
		page_content = BeautifulSoup(p.findall(str(page_content).replace('\n',''))[0])
		#Abstract
		summary.append(str(page_content.find('p', {'class':'summary'})))
		#split
		page_content = str(page_content).replace('<h2 class="article_title">', '#split#<h2 class="article_title">')
		page_content = page_content.split('#split#')
		#pop Abstract
		del page_content[0]
		#                                           "Title"  "Photo"                    "Article"
		p = re.compile('.*<h2 class=\"article_title\">(.*)</h2>(.*)<p class="article_text">(.*)<div class=\"spacer\"></div>.*')
		#                                       "Large"  "Small"    "Alt"
		photo_parse = re.compile('.*javascript.*\'(.*)\',\'(.*)\',\'(.*)\',\'.*target=\".*')
		photo_parse2 = re.compile('.*vascript.*javascript.*\'(.*)\',\'(.*)\',\'.*\',\'.*\'\);\">.*\"photo_summry\">(.*)<div\ .*')
		rm_ext_link = re.compile('<.*href.*>(.*)<.*a>(.*)')
		for i in page_content:
			Title, Photo, Article = p.findall(i)[0]
			#print Title
			summary.append('<b>' + Title + '</b><br />')

			if Photo is not '':
				if 'photo_area' in Photo:
					for i in BeautifulSoup(Photo).findAll('div',{'class':'photo_loader2'}):
						Large, Small, Alt = photo_parse.findall(str(i))[0]
						summary.append([Small, Large, Alt])
				else:
					Large, Small, Alt = photo_parse.findall(Photo)[0]
					if '640pix' not in Large:
						Large, Small, Alt = photo_parse2.findall(Photo)[0]
					summary.append([Small, Large, Alt])

			# remove external link
			if "<a href" in Article:
				rm_link = str(Article).replace('<a href', '#rm_link#<a href')
				rm_link = rm_link.split('#rm_link#')
				for i in rm_link:
					if "<a href" in i:
						url, another = rm_ext_link.findall(i)[0]
						summary.append(url)
						summary.append(another)
					else:
						summary.append(i)
			else:
				summary.append(Article)

		if DEBUG:
			print(summary)
		return ''.join(summary)

