#!/usr/bin/python
# -*- coding: utf8 -*-

from urllib import urlopen
from BeautifulSoup import BeautifulSoup
from time import gmtime, strftime, sleep, localtime
from copy import copy
from applenewsapi import apple_news_api
from socket import setdefaulttimeout
import sys, re
import urllib2
import optparse
import os
import logging

reload(sys)
sys.setdefaultencoding('utf8')

LOG_FILENAME = 'apple2rss.log'
logging.basicConfig(
	filename = LOG_FILENAME,
	level=logging.INFO, filemode = 'a',
	datefmt = '%Y-%m-%d %H:%M:%S',
	format='%(asctime)s : %(name)s : %(levelname)s\t%(message)s')

logger = logging.getLogger('apple2rss.main')


class rss_tool():
	def __init__(self, prefix_url):
		self.logger = logging.getLogger('apple2rss.rss_tool')
		self.home_url = prefix_url

	def PastHeader(self, f, classify):
		f.write('<?xml version="1.0" encoding="utf-8"?>\n')
		f.write('<rss xmlns:feedburner="http://rssnamespace.org/feedburner/ext/1.0" version="2.0">\n')
		f.write('<channel>\n')
		f.write('<title>今日蘋果新聞</title>\n')
		f.write('<link><![CDATA[http://1-apple.com.tw/index.cfm?Fuseaction=AppleSection]]></link>\n')
		f.write('<description><![CDATA[' + classify + ']]></description>\n')
		f.write('<webMaster><![CDATA[twonline@1-apple.com.tw]]></webMaster>\n')
		f.write('<rights><![CDATA[壹蘋果網絡]]></rights>\n')
		f.write('<language>zh-TW</language>\n')
		f.write('<ttl>60</ttl>\n')
		f.write('<update>' + strftime("%a, %d %b %Y %H:%M:%S") + '</update>\n')
		#f.write('<update>' + strftime("%a, %d %b %Y %H:%M:%S +0800", gmtime()) + '</update>\n')

	def PastTail(self, f):
		f.write('\n')
		f.write('</channel>\n')
		f.write('</rss>\n')

	def PastEntry(self, f, title, link, summary, classify):
		f.write('\n')
		f.write('<item>\n')
		f.write('<title><![CDATA[【' + classify + '】' + title + ']]></title>\n')
		f.write('<pubDate>' + strftime("%a, %d %b %Y %H:%M:%S") + '</pubDate>\n')
		f.write('<description><![CDATA[' + summary + ']]></description>\n')
		f.write('</item>\n')

	def CreatImgTable(self, photo):
		Title = photo.get('title')
		Small = photo.get('small')
		Big = photo.get('big')

		TableString = []
		# TableString.append('<table style="float: left; width: 30%; margin: 0 5px 5px 0; font-size: small; text-align: center;">')
		TableString.append('<table style="float: left; margin: 0 5px 5px 0; ">')
		TableString.append('<tr><td><a href="')
		TableString.append(Big)
		TableString.append('"><img title="')
		TableString.append(Title)
		TableString.append('" src="')
		TableString.append(Small)
		TableString.append('" /></td>')
		TableString.append('</tr></table>')
		return ''.join(TableString)

	def page_compose(self, content):
		compose = []

		if content.get('slide_photo') is not None:
			slide_photo = content.get('slide_photo')
		else:
			slide_photo = []

		# summary
		# the content may have no picture in summary.
		if content.get('topic_photo') is not None:
			compose.append("<img width=\"315\" src=\"" + \
				content.get('topic_photo').get('small')  + "\"/><br /></p>")

		# if content.get('slide_photo') is not None:
			# compose.append(self.CreatImgTable(slide_photo[0]))
			# slide_photo = slide_photo[1:]

		if content.get('article') is not None:
			for article in content.get('article'):
				compose.append('<br /><b>' + article['header'] + '</b><br />')
				if len(slide_photo):
					compose.append(self.CreatImgTable(slide_photo[0]))
					slide_photo = slide_photo[1:]
				compose.append(article['text'].replace('\n', '<br />'))

		if content.get('stepbox') is not None:
			for stepbox in content.get('stepbox'):
				if 'normal' is stepbox.get('type'):
					compose.append(self.CreatImgTable(stepbox.get('photo')))
					compose.append('<b>' + stepbox.get('text').get('head') + \
						'</b><br />')
					compose.append(stepbox.get('text').get('body').replace('\n', '<br />'))

				if 'puretext' is stepbox.get('type'):
					compose.append(stepbox.get('text').replace('\n', '<br />'))

				if 'threepic' is stepbox.get('type'):
					for photo in stepbox.get('photos'):
						compose.append(self.CreatImgTable(photo))

		for photo in slide_photo:
			compose.append(self.CreatImgTable(photo))

		return ''.join(compose)

	def GetPage(self, URL):
		try:
			url_req = urllib2.Request(URL)
			url_req.add_header("User-agent", "Mozilla/5.0")
			html_page = urllib2.urlopen(url_req).read()

		except IOError, ErrMsg:
			try:
				logger.warning('IOError(URL = %s) : %s, Try again', URL, ErrMsg)
				html_page = urllib2.urlopen(url_req).read() #try again
			except IOError, ErrMsg:
				logger.warning('Maybe %s is dead', URL)
				return None

		# some page only include redirect path
		page_redirect = BeautifulSoup(html_page).find('script').string
		if page_redirect is not None:
			redirect_p = re.compile('[/W]+(.*)\"')
			redirect_url = redirect_p.findall(page_redirect)[0]
			logger.info('page redirect to %s', redirect_url)
			if 'http' not in redirect_url:
				redirect_url = self.home_url + redirect_url
			return self.GetPage(redirect_url)

		return html_page

	def Url2TinyUrl(self, URL):
		return urlopen('http://tinyurl.com/api-create.php?url=' + URL).read()

	def Ch2UTF8(self, char):
		return unicode(char, 'utf-8', 'ignore')

	def write2file(self, content, file_path = '/tmp/a.html'):
		f = open(file_path, 'w')
		for i in range((len(content) / 1024) + 1):
			if((len(content) - i * 1024) > 1024):
				f.write(content[i*1024:((i+1)*1024)])
			else:
				f.write(content[i*1024:])
		f.close()

__version__ = "apple2rss Ver:0.0.1"
__author__ = "Yao-Po Wang (blue119@gmail.com)"
__USAGE__ = "usage: python %prog"

def main_argv_parser(argv):
	opt_dic = {}
	option_parser = optparse.OptionParser(usage=__USAGE__, version=__version__)
	option_parser.disable_interspersed_args()

	option_parser.add_option("-S", "--save", action="store_true", dest="save",
		help=("like as -D, not only download the news page, but also do transform."))
	option_parser.add_option("-D", "--download", action="store_true", dest="only_dl",
		help=("only to download news page don't transform to rss format."))
	option_parser.add_option("-d", "--debug", action="store_true", dest="debug",
		help=("Open debug mode"))
	option_parser.add_option("-f", "--folder", action="store", type="string",
		dest="folder", default="public_html", help=("Slecte a folder, store in.\n"
		"If it's not exist will be create. default is \"public_html\""))
	option_parser.add_option("-p", "--page", action="store", dest="page", type="string",
		help=("Convert the PAGE to rss file save in /tmp/apple.html.\n"))

	(options, args) = option_parser.parse_args(argv[1:])
	if len(args) < 2:
		# Users don't need to be told to use the 'help' command.
		#option_parser.print_help()
		#sys.exit()
		return options

	# Add manual support for --version as first argument.
	if argv[1] == '--version':
		option_parser.print_version()
		sys.exit()

	# Add manual support for --help as first argument.
	if argv[1] == '--help' or argv[1] == '-h':
		option_parser.print_help()
		sys.exit()

	return options

def mkdir(path, delete):
	if os.path.isdir(path):
		if delete:
			logger.info("delete -> %s",  path)
			os.rmdir(path)
			logger.info("create: %s",  path)
			os.mkdir(path)
	else:
		logger.info("create: %s",  path)
		os.mkdir(path)

if __name__ == '__main__':
	opt = main_argv_parser(sys.argv)
	from applenewsapi import apple_news_api


	if opt.page is not None:
		news_api = apple_news_api()
		rss_api = rss_tool(news_api.home_url)
		#f = open(opt.page, "r")
		#PageContent = f.readlines()
		PageContent = rss_api.GetPage(opt.page)
		#PageContent = BeautifulSoup(''.join(PageContent))
		PageContent = news_api.page_parser(PageContent)
		PageContent = rss_api.page_compose(PageContent)
		# PageContent = '<h1>' + title + '</h1>' + PageContent
		rss_api.write2file(PageContent, 'main_story.html')
		sys.exit()

	#folder create
	store_in = opt.folder + "/" + strftime("%Y-%m-%d", localtime())
	mkdir(opt.folder, False)
	mkdir(store_in, False)

	"""
	Reference:
		HOWTO Fetch Internet Resources with Python: http://www.voidspace.org.uk/python/articles/urllib2.shtml
	"""
	# some connection timeout in seconds
	timeout = 10
	setdefaulttimeout(timeout)

	news_api = apple_news_api()
	news_api.get_list()
	news_api.show_news_list()

	rss_api = rss_tool(news_api.home_url)

	if opt.debug:
		title = news_api.news_lists[rss_api.Ch2UTF8('頭條要聞')][0][1]['title']
		logger.debug('Get [%s]', title)
		PageContent = rss_api.GetPage(news_api.home_url + \
			news_api.news_lists[rss_api.Ch2UTF8('頭條要聞')][0][1]['href'])
		# sys.stdout.write('[Parsing] -> ')
		logger.debug('[Parsing] -> ')
		PageContent = news_api.page_parser(PageContent)
		# sys.stdout.write('[Compose] -> ')
		logger.debug('[Compose] -> ')
		PageContent = rss_api.page_compose(PageContent)
		PageContent = '<h1>' + title + '</h1>' + PageContent
		# print('[Write2File]')
		logger.debug('[Write2File]')
		rss_api.write2file(PageContent, 'main_story.html')
	else:
		RssFileName = {
			rss_api.Ch2UTF8('頭條要聞'):'HeadLine',
			rss_api.Ch2UTF8('副刊'):'Supplement',
			rss_api.Ch2UTF8('體育'):'Sport',
			rss_api.Ch2UTF8('蘋果國際'):'International',
			rss_api.Ch2UTF8('娛樂'):'Entertainment',
			rss_api.Ch2UTF8('財經'):'Finance',
			rss_api.Ch2UTF8('地產'):'Estate',
			rss_api.Ch2UTF8('豪宅與中古'):'LuxSecHouse',
			rss_api.Ch2UTF8('家居王'):'HouseWorking'
		}

		if opt.only_dl:
			for Classify in news_api.news_lists:
				ClassifyPath = store_in + "/" + RssFileName[Classify]
				mkdir(ClassifyPath, True)
				print '\n------------- ' + Classify + ' -------------'
				for NewsList in news_api.news_lists[Classify]:
					f = open(ClassifyPath + "/" + NewsList['href'].split('/')[-3] + '.html', 'w')

					PageContent = rss_api.GetPage(news_api.home_url + NewsList['href'])
					print 'Get ->' + '【' + NewsList['subClassify'] + '】' + NewsList['title']

					rss_api.write2file(str(PageContent), f.name)

					f.close()
					sleep(1)
					#print ''.join(summary)
			sys.exit()

		#NewsChunksDict debug
		#for ClassifyName in NewsChunksDict:
		#	print '------------- ' + ClassifyName + ' -------------'
		#	for NewsList in NewsChunksDict[ClassifyName]:
		#		print '【' + NewsList['subClassify'] + '】' + NewsList['Title'] + NewsList['HREF']
		PageContent = []
		for Classify in news_api.news_lists:
			try:
				f = open(store_in + "/" + RssFileName[Classify] + '_RSS.html', 'w')
			except KeyError:
				logger.info('%s, not support' % (Classify))
				continue
			rss_api.PastHeader(f, str(Classify))
			logger.info('------------- %s -------------', Classify)
			for NewsList in news_api.news_lists[Classify]:
				subClassify = NewsList[0]
				# print subClassify
				for news_item in NewsList[1:]:
					try:
						PageContent = rss_api.GetPage(news_api.home_url + news_item['href'])
					except IOError:
						#try again
						try:
							PageContent = rss_api.GetPage(news_api.home_url + news_item['href'])
						except IOError:
							#abandent
							continue
					logger.info('【' + subClassify + '】' + news_item['title'])
					summary = []

					try:
						result =  news_api.page_parser(PageContent)
					except:
						logger.critical('parse failur %s%s', news_api.home_url, news_item['href'])
						continue

					try:
						summary.append(rss_api.page_compose(result))
					except:
						logger.critical('compose failur %s%s', news_api.home_url, news_item['href'])
						logger.critical('Dump:')
						logger.critical(str(result))
						continue

					#summary = [s for s in summary if s != None]
					rss_api.PastEntry(f, news_item['title'], news_api.home_url + news_item['href'], ''.join(summary), subClassify)
					sleep(1)
					#print ''.join(summary)
			rss_api.PastTail(f)
			f.close()

