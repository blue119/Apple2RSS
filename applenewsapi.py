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
import logging

reload(sys)
sys.setdefaultencoding('utf8')
logger = logging.getLogger('apple2rss.api')


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
			logger.info('<<< ' + classfied + ' >>>')#classified title
			for sub_classified in self.news_lists.get(classfied):
				sub_title =  sub_classified[0]
				for news_item in sub_classified[1:]:
					logger.info('[' + sub_title + '] ' + news_item['title'] + ' : ' + news_item['href'])
			# print ''

	def string_strip(self, string):
		'''
		avoid p tag and space
		change <br /> to '\n'
		'''
		strip_p_p = re.compile("<p.*?>(.*)</p.*?>")
		string = strip_p_p.findall(string)[0]
		string = string.replace('\n', '').replace('\r', '')
		string = string.replace('<br />', '\n').replace('  ', '')
		if len(string):
			if string[0] == '\n':
				string = string[1:]
			if string[-1] == '\n':
				string = string[:-1]
		return string

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

	def totally_list_dump(self, totally):
		if totally.get('topic_photo') is not None:
			logger.debug('===== topic photo =====')
			logger.debug(totally.get('topic_photo').get('small'))

		if totally.get('article') is not None:
			logger.debug('===== article =====')
			for article in totally.get('article'):
				logger.debug('header : ' +  article['header'])
				logger.debug('text : ' +  article['text'])

		if totally.get('stepbox') is not None:
			logger.debug('===== stepbox =====')
			for stepbox in totally.get('stepbox'):
				if 'normal' is stepbox.get('type'):
					photo = stepbox.get('photo')
					logger.debug('type : %s', stepbox.get('type'))
					logger.debug('title : %s', photo.get('title'))
					logger.debug('big  : %s', photo.get('big'))
					logger.debug('small : %s', photo.get('small'))
					text = stepbox.get('text')
					logger.debug('head : %s', text.get('head'))
					logger.debug('body : %s', text.get('body'))

				if 'puretext' is stepbox.get('type'):
					logger.debug('type : %s', stepbox.get('type'))
					logger.debug('text : %s', stepbox.get('text'))

				if 'threepic' is stepbox.get('type'):
					logger.debug('type : %s', stepbox.get('type'))
					for photo in stepbox.get('photos'):
						logger.debug('title : %s', photo.get('title'))
						logger.debug('big  : %s', photo.get('big'))
						logger.debug('small : %s', photo.get('small'))

		if totally.get('slide_photo') is not None:
			logger.debug('===== slide photo =====')
			for photo in totally.get('slide_photo'):
				logger.debug('title : %s', photo.get('title'))
				logger.debug('big  : %s', photo.get('big'))
				logger.debug('small : %s', photo.get('small'))

	def get_list(self):
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
		title_href = re.compile('<a.*"(.*)">(.*)</a>')
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
			# logger.info('+++++ ' + classified_title + ' +++++')

			# ------------------------------------------------
			# a special case for "頭條" sub_classified
			if 'h2' not in str(top):
				sub_classified_list = []
				sub_classified_list.append(top.findNext('h2').string)
				for news in top.findNext('ul').findAll('a'):
					href, title = title_href.findall(str(news))[0]
					title = title.replace('', '').replace('<br />', '').replace('…', '')
					# logger.info( '\t' + title + ' - ' + href)

					news_item['title'] = title
					news_item['href'] = href
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
						href, title = title_href.findall(str(news))[0]
						title = title.replace('', '').replace('<br />', '').replace('…', '')
						# logger.info( '\t' + title + ' - ' + href)

						news_item['title'] = title
						news_item['href'] = href
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
					href, title = title_href.findall(str(news))[0]
					title = title.replace('', '').replace('<br />', '').replace('…', '')
					# logger.info( '\t' + title + ' - ' + href)

					news_item['title'] = title
					news_item['href'] = href
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

	def page_parser(self, raw_content):
		"""
	{article_dict} : {'header' : string, 'text' : string}

	the struct of photo
		photo['title'] -> title
		photo['small'] -> src
		photo['big'] -> href

	return struct of totally list:
	{
	  'topic_photo' : {photo},
	  'article' : [{article_dict}, {article_dict}, ...],
	  'slide_photo' : [{photo}, {photo}, ...]
	  'stepbox' : [{'type' : 'normal', 'photo' : {photo},
	                                   'text' : {'head' : head, 'body' : text}}
	               {'type' : 'threepic', 'photos' : [{photo}, {photo{ ..}]
	  			   {'type' : 'puretext', 'text' : string} ]
	}
		"""

		totally = {}
		photo = {}
		photo_lists = []
		article_raw = []
		article_dict = {}

		# data pre-process
		start = 0
		for string in raw_content.split('\n'):
			if 'iclickAdBody_End' in string:
				break
			if start:
				article_raw.append(string)
			if 'class' in string and 'summary' in string:
				start = 1

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

		# append other photo
		if len(photo_lists) > 0:
			totally['slide_photo'] = copy(photo_lists)

		# article mining
		article = []
		article_p = re.compile("<h2.*\">(.*)\<\/h2\>.*article_text\">(.*)</p>")
		summary_p = re.compile(".*summary\">(.*)<h2.*")
		strip_garbage = re.compile("(.*)<!")
		strip_h1_p = re.compile("<h1.*?>(.*)</.*?>")
		strip_h2_p = re.compile("<h2.*?>(.*)</.*?>")

		article_paragraph = content.find('article', {'class' : 'article_paragraph'})
		# article.append(str(article_paragraph.h1)) # topic
		#strip h2 tag for sub topic
		article_dict['header'] = strip_h2_p.findall(str(article_paragraph.h2))[0]

		#find article photo at top
		if article_paragraph.find('img') is not None:
			img_src = article_paragraph.find('img')['src']
			if 'apple60x60_R.gif' not in img_src:
				photo['title'] = ''
				photo['small'] = article_paragraph.find('img')['src']
				photo['big'] = ''
				if totally.get('slide_photo') is None:
					totally['slide_photo'] = copy([photo])
				else:
					totally['slide_photo'].insert(0, copy([photo]))
			else:
				pass

		#found summary
		summary = str(article_paragraph.find('p', {'class':'summary'}))
		summary = summary.replace('\n', '').replace('\r', '')
		summary = summary.replace('\t', '').replace('  ', '')
		summary = summary_p.findall(summary)[0]
		article_dict['text'] = summary.replace('<br />', '\n')
		totally['article'] = [copy(article_dict),] # append summary


		# resorting
		# content = article_paragraph.find('div', {'id' : 'article_content'})
		content = article_paragraph.find('div', {'class' : 'article_paragraph_box'})
		# new line free
		content_sp = str(content).replace('\n', '').replace('\r', '')
		# tab and space free
		content_sp = content_sp.replace('\t', '').replace('  ', '')
		# split
		content_sp = content_sp.replace('<h2 id=\"article_title', 'XXXXX<h2 ').split('XXXXX')


		# finding paragraph
		for i in content_sp[1:]:
			h2, string = article_p.findall(i)[0]
			article_dict['header'] = h2
			#avoid garbage info
			if '.gif' in string:
				string = ''
				continue
			# article.append(string)
			article_dict['text'] = string.replace('<br />', '\n')
			totally['article'].append(copy(article_dict))

		# process stepbox
		stepbox = BeautifulSoup(''.join(article_raw)).find('div')
		if stepbox is not None:
			totally['stepbox'] = []

		# puretext
		# normal : text + photo
		# threepic
		while(stepbox):
			box_bulk = {}
			if 'normal' in str(stepbox.get('class')):
				string_builk = ''
				text_dict = box_bulk['text'] = {}
				photo['title'] = stepbox.a['title']
				photo['small'] = stepbox.a.img['src']
				photo['big'] = stepbox.a['href']
				box_bulk['type'] = 'normal'
				box_bulk['photo'] = copy(photo)
				# strip h1 header and plus bold tag
				text_dict['head'] = strip_h1_p.findall(str(stepbox.h1))[0]
				for string in stepbox.findAll('p'):
					string_builk += self.string_strip(str(string))
				text_dict['body'] = string_builk

			if 'puretext' in str(stepbox.get('class')):
				box_bulk['type'] = 'puretext'
				box_bulk['text'] = self.string_strip(str(stepbox.p))

			if 'threepic' in str(stepbox.get('class')):
				box_bulk['type'] = 'threepic'
				box_bulk['photos'] = []
				for i in stepbox.findAll('a'):
					photo['title'] = i['title']
					photo['small'] = i['href']
					photo['big'] = i.img['src']
					box_bulk['photos'].append(copy(photo))

			totally['stepbox'].append(copy(box_bulk))
			stepbox = stepbox.findNext('div')

		# totally['article'] = (''.join(article)) # append article

		self.totally_list_dump(totally)

		return totally

