#!/usr/bin/python
# -*- coding: utf8 -*-

#v0.1 can be run but not is good.
#v0.2 patch to support new format

from urllib import urlopen
from BeautifulSoup import BeautifulSoup
from News import NewsBase
from collections import OrderedDict
from time import gmtime, strftime, sleep
from copy import copy
import sys, re
import urllib2
import logging

reload(sys)
sys.setdefaultencoding('utf8')
logger = logging.getLogger('apple2rss.api')

class AppleNews(NewsBase):
	""" the api originally is my private using to grabe news from nextmedia web
	side. then, convert to RSS format and exclude every ad.
	"""
	def __init__(self, io, url):
		super(AppleNews, self).__init__(url)
		self._io = io
		self._news_lists = {}

	@property
	def home_url(self):
		"""docstring for home_url"""
		return self._url

	@property
	def news_lists(self):
		"""docstring for news_lists"""
		return self._news_lists

	def get_page(self, url):
		return self._io.open(url)

	def get_list(self, path):
		""" get all lists of news from apple daily.
		return struct of dict:
			{subject: {sub-subject: { title: url, title: url, ...}, }, } """

		# lists init
		self._news_lists = {}

		lists_token_start = '<!-- News -->'
		lists_token_end = '<aside id="sitesidecontent" class="manu lvl">'
		catalog_page = self.get_page( self._url + path)
		lists_section = catalog_page.split(lists_token_start)[1]
		lists_section = lists_section.split(lists_token_end)[0]

		# sweep out all incorrect end-tag
		end_tag = "</section>                                  <article"
		lists_section = ''.join(lists_section.split('\n'))
		lists_section = lists_section.replace(end_tag, '<article')
		lists_section = BeautifulSoup(lists_section)

		titles_sec_token = 'section-news-tab-menu'
		anchor_title = re.compile('#([\w\-]+).*>(.*)<.*')
		title_href = re.compile('<a href="(.*)" title="(.*)">.*</a>')
		subject_titles = BeautifulSoup(catalog_page)
		subject_titles = subject_titles.find("div", {"id": titles_sec_token})

		#get classify
		classified_lists = {}
		for cl in  subject_titles.findAll('li'):
			title = cl.a.string
			classified_lists[title] = cl["id"]

		# http://docs.python.org/dev/whatsnew/2.7.html#pep-0372
		for anchor in classified_lists.itervalues():
			sub_classified_set = []
			top = lists_section.find('section', {'id' : anchor})
			h1 = top.h1.string.replace('&nbsp;', '')
			logger.debug("%s %s %s" % ('+' * 5,  h1, '+' * 5))

			h2_dict = OrderedDict()
			for article in top.findAll('article'):
				h2 = article.h2.string

				h2_list = []
				news_item = {}
				for news in article.findAll('a'):
					href, title = title_href.findall(str(news))[0]
					title = title.replace('', '').replace('<br />', '').replace('…', '')
					logger.debug( '[' + h2 + '] ' + title + ' - ' + href)

					news_item['title'] = title
					news_item['href'] = href[1:]
					h2_list.append(copy(news_item))
				h2_dict[h2] = copy(h2_list)
			self._news_lists[h1] = copy(h2_dict)

	def show_news_list(self):
		for classfied in self.news_lists:
			logger.info('<<< ' + classfied + ' >>>')#classified title
			for sub_classified in self.news_lists.get(classfied):
				sub_title =  sub_classified[0]
				for news_item in sub_classified[1:]:
					logger.info('[' + sub_title + '] ' + news_item['title'] + ' : ' + news_item['href'])

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

	def page_parser(self, raw_content):
		""" {article_dict} : {'header' : string, 'text' : string}

	the struct of photo
		photo['title'] -> title
		photo['small'] -> src
		photo['big'] -> href

	return struct of totally list:
	{
	  'an_photo' : {photo},
	  'an_video' : mp4,
	  'h1' : h1,
	  'h2' : h2,
	  'article' : [{article_dict}, {article_dict}, ...],
	  'slide_photo' : [{photo}, {photo}, ...]
	}
		"""
		totally = {}
		article_dict = {}
		d = BeautifulSoup(raw_content)

		# look for the photo of action news
		strip_an_p = re.compile("\[{url:'(.*)'}\].*Player.*\('(.*)'\);")
		if d.find('div', {'id':'videobox'}):
			photo = {}
			an_url = d.find('div', {'id':'videobox'}).iframe["src"]

			an_page = urlopen(an_url).read()

			# just leave mp4 and jpg information
			an_page = ''.join(an_page)
			an_page = an_page.split("var playlist_array = ")[1]
			an_page = an_page.split("var new_playlist_array")[0]
			an_page = an_page.replace('\n', '').replace(' ', '')
			mp4, jpg = strip_an_p.findall(an_page)[0]

			photo['title'] = ""
			photo['big'] = ""
			photo['small'] = jpg
			totally["an_photo"] = copy(photo)
			totally["an_video"] = mp4

		# main section of article
		article = d.find('article', {'class':'mpatc clearmen'})
		article_dict = {}
		totally["article"] = []

		totally['h1'] = d.find('h1', {'id':'h1'}).string
		totally['h2'] = d.find('h2', {'id':'h2'}).string

		# grab the article of intro
		strip_intro_p = re.compile("<p\ id=\"introid\">(.*)</p>")
		intro = article.find('p', {'id':'introid'})
		if intro: # some article have no intro
			intro = strip_intro_p.findall(str(intro))[0]
			totally["article"].append({"header":"", "text":intro})

		# look for brlockcontent
		blockhead = 0
		strip_p_p = re.compile("<p\ id=\"blockcontent[\d]+\">(.*)</p>")
		next = article.find('h2', {'id':'blockhead' + str(blockhead)})
		while(next):
			blockhead += 1
			header = next.string

			next = next.findNext('p')
			text = strip_p_p.findall(str(next))[0]
			text = text.replace("<br />", "")

			totally["article"].append({"header": header if header else "", \
					"text": text if text else ""})

			next = next.findNext('h2', {'id':'blockhead' + str(blockhead)})

		# look for all figure
		next = article.find('figure', {'class':'lbimg sgimg sglft'})
		strip_annoy_href_p = re.compile(".*href=\"(.*)\"><img\ .*")
		totally['slide_photo'] = []
		while(next):
			photo = {}

			# sweep out annoying word
			# if photo string that include annoying word
			if "&lt;BR&gt;" in str(next):
				annoy = str(next).replace("&lt;BR&gt;", "").replace("<br />", "")
				photo['big'] = strip_annoy_href_p.findall(annoy)[0]
				annoy = BeautifulSoup(annoy)
				photo['title'] = annoy.a["title"]
				photo['small'] = annoy.img["src"]
			else:
				# look for title of figure and big size figure
				next = next.findNext('a')
				photo['title'] = next["title"]
				photo['big'] = next["href"]

				# look for small size figure
				next = next.findNext('img')
				photo['small'] = next["src"]

			totally['slide_photo'].append(copy(photo))
			next = next.findNext('figure', {'class':'lbimg sgimg sglft'})

		return totally

