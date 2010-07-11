#!/usr/bin/python
# -*- coding: utf8 -*-

#v0.1 can be run but not is good.
#v0.2 patch to support new format

from urllib import urlopen
from BeautifulSoup import BeautifulSoup
from time import gmtime, strftime, sleep
from copy import copy
import sys, re
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

	def show_news_list(self):
		for i in self.news_list:
			print '<<< ' + i + ' >>>'
			for j in self.news_list[i]:
				print '[' + j['subClassify'] + '] ' + j['title']
			print ''

	def get_title(self, PageContent):
		p = re.compile('^<title>(.*)\ \|\ .*\ \|\ .*\ \|.*\|.*</title>')
		Title = p.findall(str(PageContent.title).replace('\n', ''))
		try:
			return Title[0]
		except IndexError:
			print 'Can not parsing this title : "' + str(PageContent.title) + '"'
			Title = None
			return Title

	def ex_html_tag(self, s):
		tmp_s = re.split('>', s.replace(' ', ''))
		tmp = []
		for i in tmp_s[:-1]:
			tmp.append(re.compile('(.*)\<.*').findall(i)[0])
		return ''.join(tmp)

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
					news_contents.append(copy(news_items))
				counting += 1
			self.news_list[classify_by_name] = copy(news_contents)
			news_contents = []
		
	def page_parser(self, content, DEBUG=False):
		"""
		return format:
			[{summery}, {article}, ...]

		summery
			temp_dic['title'] -> string
			temp_dic['pic'] -> ['title', 'small img', 'big img']
			temp_dic['summary'] -> string

		article
			temp_dic['article_title'] -> string
			temp_dic['photo'] -> ['title', 'small img', 'big img'] || temp_dic['photo_area'] -> [temp_dic['photo'], ...]
			temp_dic['article_text'] -> string
		"""
		summary = []
		temp_dic = {}
		temp_dic['title'] = '<b>' + self.get_title(content) + '</b>'
		if DEBUG:
			print('Title: %s' % self.get_title(content))

		# grab active movie's backgroup pic
		try:
			am_img = str(content.find('div', {'id':'videoplayer'}).find('script'))
			temp_dic['am_pic'] = self.home_url + re.compile(".*AV_IMAGE2\s*?\=\s*?\"\/(.*\.jpg)\"\;.*").findall(am_img)[0]
		except:
			pass

		if DEBUG and temp_dic.get('am_pic') is not None:
			print "am pic: " + temp_dic.get('am_pic')


		page_content = content.find('div', {'id':'article_left'})
		# lots of page have no tag for page_content
		if page_content is None:
			page_content = content
		
		# grab story picture
		try:
			img = str(page_content.find('script', {'language':'javascript'}))

			p = re.compile(".*g_Image.*javascript.*\([\"|\'](http.*\.jpg)[\"|\']\,\s*?[\"|\'](http.*.jpg)[\"|\']\,\s*?[\"|\'](.*)[\"|\']\,\s*?.*swf.*")
			# group 1: BigIMG
			#group 2: SmallIMG
			# group 3: titleIMG 

			result = p.findall(img)
			BigIMG, SmallIMG, titleIMG = result[0]
			temp_dic['pic'] = [titleIMG, SmallIMG, BigIMG]
		except: #No Picture in intro
			pass

		if DEBUG:
			if temp_dic.get('pic') is not None:
				print "story pic: "
				for i in temp_dic.get('pic'):
					print "\t" + i
			else:
				print 'No store picture.'

		#Grab alticl section
		p = re.compile('.*iclickAdBody_Start\"\>\<\/span\>(.*)\<span\ name\=\"iclickAdBody_End\"\ id\=.*')
		page_content = BeautifulSoup(p.findall(str(page_content).replace('\n',''))[0])

		#Abstract
		result = re.compile("^\<.*\"\>\s+?(\S.*)\<\/p\>").findall(str(page_content.find('p', {'class':'summary'})))
		if len(result):
			temp_dic['summary'] = re.compile("^\<.*\"\>\s+?(\S.*)\<\/p\>").findall(str(page_content.find('p', {'class':'summary'})))[0]
		
		# append to summary list
		summary.append(copy(temp_dic))
		temp_dic.clear()

		if DEBUG:
			print 'Summary: '
			print summary[0].get('summary')

		#split
		page_content = str(page_content).replace('<h2 class="article_title">', '#split#<h2 class="article_title">')
		page_content = page_content.split('#split#')

		#                                           "Title"  "Photo"                    "Article"
		p = re.compile('.*<h2 class=\"article_title\">(.*)</h2>(.*)<p class="article_text">(.*)<div class=\"spacer\"></div>.*')
		#                                       "Large"  "Small"    "Alt"
		photo_parse = re.compile('.*javascript.*\'(.*)\',\'(.*)\',\'(.*)\',\'.*target=\".*')
		photo_parse2 = re.compile('.*vascript.*javascript.*\'(.*)\',\'(.*)\',\'.*\',\'.*\'\);\">.*\"photo_summry\">(.*)<div\ .*')
		rm_ext_link = re.compile('<.*href.*>(.*)<.*a>(.*)')

		for i in page_content[1:]: # void summary
			Title, Photo, Article = p.findall(i)[0]

			#print '\n==========================='
			#print "Title: \n\t" + Title
			#print "Photo: \n\t" + Photo
			#print "Artic: \n\t" + Article

			#print Title
			temp_dic['article_title'] = '<p><b>' + Title + '</b><br />'

			if Photo is not '':
				if 'photo_area' in Photo:
					temp_dic['photo_area'] = []
					for i in BeautifulSoup(Photo).findAll('div',{'class':'photo_loader2'}):
						Large, Small, Alt = photo_parse.findall(str(i))[0]
						temp_dic['photo_area'].append([Alt, Small, Large])
				else:
					Large, Small, Alt = photo_parse.findall(Photo)[0]
					if '640pix' not in Large:
						Large, Small, Alt = photo_parse2.findall(Photo)[0]
					temp_dic['photo'] = [Alt, Small, Large]
			
			temp_dic['article_text'] = ''
			# remove external link
			if "<a href" in Article:
				rm_link = str(Article).replace('<a href', '#rm_link#<a href')
				rm_link = rm_link.split('#rm_link#')
				for i in rm_link:
					if "<a href" in i:
						url, another = rm_ext_link.findall(i)[0]
						temp_dic['article_text'] += url + another
					else:
						temp_dic['article_text'] += i
			else:
				temp_dic['article_text'] += Article

			summary.append(copy(temp_dic))
			
			if DEBUG:
				print '\n==========================='
				print "Title: \n\t" + temp_dic.get('article_title')
				if temp_dic.get('photo'):
					print "Photo: "
					for i in temp_dic.get('photo'):
						print "\t" + i
				print "Artic: \n\t" + temp_dic.get('article_text')

			temp_dic.clear()

		if DEBUG:
			print(summary)

		return summary

