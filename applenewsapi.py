#!/usr/bin/python
# -*- coding: utf8 -*-

#v0.1 can be run but not is good.
#v0.2 patch to support new format

from urllib import urlopen
from BeautifulSoup import BeautifulSoup
from time import gmtime, strftime, sleep
from copy import copy
# from xpinyin.xpinyin import Pinyin
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
		self.news_lists = {}
		self.home_url = 'http://tw.nextmedia.com/'
		#self.catalog_page = unicode(AppleNewHome, 'big5', 'ignore')
		self.catalog_page = urlopen( self.home_url + 'applenews/todayapple').read()
		self.catalog_page = BeautifulSoup(self.catalog_page)

	def show_news_list(self):
		for classfied in self.news_lists:
			print '<<< ' + classfied + ' >>>'#classified title
			for sub_classified in self.news_lists.get(classfied):
				sub_title =  sub_classified[0]
				for news_item in sub_classified[1:]:
					print '\t' + '[' + sub_title + '] ' + news_item['title'] + ' : ' + news_item['href']
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
		the struct of classification_lists :
			{title : anchor, ...}

		the struct of news_item :
			{'title' : news_title, 'href' : news_href}

		the struct of news_item_set :
			[news_item, news_item, ...]

		the struct of sub_classified_list :
			[subclassified_title, news_item_set]

		the struct of sub_classified_set :
			[sub_classified_list, ...]

		the struct of news_lists :
			{classified_title : sub_classified_set, ...}
		"""
		#pinyin = Pinyin("xpinyin/Mandarin.dat") #zh_tw utf-8 to pinyin

		anchor_title = re.compile('#([\w\-]+).*>(.*)<.*')
		find_classified_section_id = 'section-news-tab-menu'
		find_subclassified_section_class = 'left_news_block_sqz'

		self.news_lists = {}
		classified_lists = {}
		sub_classified_list = []
		news_item = {}
		news_item_set = []
		sub_classified_set = []

		#get classify
		for cl in  self.catalog_page.find('div', {'id' : find_classified_section_id}).findAll('a'):
			anchor, title = anchor_title.findall(str(cl))[0]
			classified_lists[title] = anchor

		for anchor in classified_lists.itervalues():
			sub_classified_set = []
			top = self.catalog_page.find('div', {'class' : find_subclassified_section_class, 'id' : anchor})
			classified_title = top.h1.string
			# print '+++++ ' + classified_title + ' +++++'

			# ------------------------------------------------
			# a special case for "頭條" sub_classified
			if 'h2' not in str(top):
				sub_classified_list = []
				sub_classified_list.append(top.findNext('h2').string)
				for news in top.findNext('ul').findAll('a'):
					news_item['title'] = news.string.replace('…', '')
					news_item['href'] = news['href']
					sub_classified_list.append(copy(news_item))
				sub_classified_set.append(copy(sub_classified_list))

			# ------------------------------------------------
			# normally, h1 include a h2 and it's news items
			# in "副刊", there are a parsing issus. whole h2 items be included h1 scope.
			for sub_classified in top.findAll('figure'):
				sub_classified_list = []
				if sub_classified.h2 is not None:
					# print sub_classified.h2.string
					sub_classified_list.append(sub_classified.h2.string)
					# grab news items in sub classified
					for news in sub_classified.ul.findAll('a'):
						#print '\t' + news.string.replace('…', '') + ' - ' + news['href']
						news_item['title'] = news.string.replace('…', '')
						news_item['href'] = news['href']
						sub_classified_list.append(copy(news_item))
					sub_classified_set.append(copy(sub_classified_list))

			# ------------------------------------------------
			# grab other sub_classified not be included <h1>
			sub = top.findNext('div', {'class' : find_subclassified_section_class, 'id' : anchor})
			while(sub):
				sub_classified_list = []
				# print sub.h2.string
				sub_classified_list.append(sub.h2.string)
				for news in sub.ul.findAll('a'):
					#print '\t' + news.string.replace('…', '') + ' : ' + news['href']
					news_item['title'] = news.string.replace('…', '')
					news_item['href'] = news['href']
					sub_classified_list.append(copy(news_item))
				sub_classified_set.append(copy(sub_classified_list))
				sub = sub.findNext('div', {'class' : find_subclassified_section_class, 'id' : anchor})
			# ------------------------------------------------
			self.news_lists[classified_title] = copy(sub_classified_set)

		# for classfied in self.news_lists:
			# print classfied #classified title
			# for sub_classified in self.news_lists.get(classfied):
				# print '\t' + sub_classified[0]
				# for news_item in sub_classified[1:]:
					# print '\t\t' + news_item['title'] + ' : ' + news_item['href']

	def page_parser(self, raw_content, DEBUG=False):
		"""
		return struct of totally list:
			{'topic_photo' : {photo}, 'article' : str(article_string), 'slide_photo' : [{photo}, {photo}, ...]}

		the struct of photo
			photo['title'] -> title
			photo['small'] -> src
			photo['big'] -> href

		"""

		totally = {}

		photo_lists = []
		photo = {}

		# data pre-process
		content = BeautifulSoup(raw_content)

		# find artvideo_photo
		if content.find('div', {'id' : 'videobox'}) is not None:
			# there is artvideo tag
			tmp_str = str(content.find('div', {'id' : 'videobox'}).find('script', {'type' : 'text/javascript'}))
			artvideo_photo_p = re.compile("image[\'\,\'\ ]+([\w\:\/\.]+)")
			photo['small'] = artvideo_photo_p.findall(tmp_str)[0]
			photo['title'] = ''
			photo['big'] = ''
			totally['topic_photo'] = copy(photo)

		# photo mining
		next = content.find('div', {'class' : 'each_slide'})
		while(next):
			photo['title'] = next.a['title']
			photo['small'] = next.a.img['src']
			photo['big'] = next.a['href']
			photo_lists.append(copy(photo))
			next = next.findNext('div', {'class' : 'each_slide'})

		# try to add a photo become topic photo, if it have no artvideo photo and have photo slide.
		if totally.get('topic_photo') is None and len(photo_lists) > 0:
			totally['topic_photo'] = copy(photo_lists[0]) # append topic photo
			photo_lists = photo_lists[1:] # shift

		# append other photo
		if len(photo_lists) > 0:
			totally['slide_photo'] = copy(photo_lists)

		# article mining
		article = []
		article_p = re.compile("<h2.*\">(.*)\<\/h2\>.*article_text\">(.*)</p>")
		summary_p = re.compile("<div.*summary\">(.*)")
		strip_garbage = re.compile("(.*)<!")

		article_paragraph = content.find('article', {'class' : 'article_paragraph'})
		article.append(str(article_paragraph.h1)) # topic
		article.append(str(article_paragraph.h2)) # sub topic

		# resorting
		# content = article_paragraph.find('div', {'id' : 'article_content'})
		content = article_paragraph.find('div', {'class' : 'article_paragraph_box'})
		# new line free
		content_split = str(content).replace('\n', '').replace('\r', '')
		# tab and space free
		content_split = content_split.replace('\t', '').replace('  ', '')
		# split
		content_split = content_split.replace('<h2 id=\"article_title', 'XXXXX<h2 ').split('XXXXX')

		# article.append(summary_p.findall(content_split[0])[0]) #summary
		strip = summary_p.findall(content_split[0])[0]

		# strip like as <!--單圖文字 -->
		if '<!' in strip:
			strip = strip_garbage.findall(strip)[0]

		article.append(strip)

		# finding paragraph
		for i in content_split[1:]:
			h2, string = article_p.findall(i)[0]
			# article.append("<h2>" + h2 + "</h2>")
			article.append("<br /><b>" + h2 + "</b>")
			#avoid garbage info
			if '.gif' in string:
				string = ''
			article.append(string)

		totally['article'] = (''.join(article)) # append article

		if DEBUG:
			print(totally)

		return totally

