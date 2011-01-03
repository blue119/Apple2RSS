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

reload(sys)
sys.setdefaultencoding('utf8')

class rss_tool():
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
		#f.write('<pubDate>' + strftime("%a, %d %b %Y %H:%M:%S +0800", gmtime()) + '</pubDate>\n')
		#f.write('<author><![CDATA[' + subclassify +']]></author>\n')
		#f.write('<link><![CDATA[' + link + ']]></link>\n')
		f.write('<description><![CDATA[' + summary + ']]></description>\n')
		f.write('</item>\n')

	def CreatImgTable(self, photo_list = ['', '', '']):
		titleIMG, SmallIMG, BigIMG = photo_list
		if '.svg' in SmallIMG:
			SmallIMG = HomeUrl + SmallIMG[1:]
		if '.svg' in BigIMG:
			BigIMG = HomeUrl + BigIMG[1:]
		TableString = []
		TableString.append('<table style="float: left; width: 30%; margin: 0 5px 5px 0; font-size: small; text-align: center;">')
		TableString.append('<tr><td><a href="')
		TableString.append(BigIMG)
		TableString.append('"><img title="')
		TableString.append(titleIMG)
		TableString.append('" src="')
		TableString.append(SmallIMG)
		TableString.append('" /></td></tr></table>')
		return ''.join(TableString)

	def page_compose(self, content):
		compose = []
		# summary
		#compose.append(content[0]['title'])
		# the content may have no picture in summary.
		if content[0].get('am_pic') is not None:
			compose.append("<img width=\"315\" src=\"" + content[0].get('am_pic')  + "\"/><br /></p>")

		if 'pic' in content[0].keys():
			compose.append(self.CreatImgTable(content[0]['pic']))

		if content[0].get('summary') is not None:
			compose.append(content[0].get('summary'))

		for i in content[1:]:
			#extract photo
			if 'photo_area' not in i.keys():
				if 'photo' in i.keys():
					compose.append(self.CreatImgTable(i['photo']))
			else:
				for j in i['photo_area']:
					compose.append(self.CreatImgTable(j))
			#extract title
			compose.append(i['article_title'])
			#extract text
			compose.append(i['article_text'])
		return ''.join(compose)

	def GetPage(self, URL):
		try:
			url_req = urllib2.Request(URL)
			url_req.add_header("User-agent", "Mozilla/5.0")
			html_page = urllib2.urlopen(url_req).read()
		except IOError, ErrMsg:
			try:
				print 'IOError(URL = %s) : %s, Try again\n', URL, ErrMsg
				html_page = urllib2.urlopen(url_req).read() #try again
			except IOError, ErrMsg:
				print 'Maybe %s is dead\n', URL
				return None
		return BeautifulSoup(html_page)

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
							dest="folder", default="public_html",
							help=("Slecte a folder, store in.\n"
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
			print "delete -> " + path
			os.rmdir(path)
			print "create: " + path
			os.mkdir(path)
	else:
		print "create: " + path
		os.mkdir(path)

if __name__ == '__main__':
	opt = main_argv_parser(sys.argv)
	from applenewsapi import apple_news_api

	if opt.page is not None:
		rss_api = rss_tool()
		news_api = apple_news_api()
		#f = open(opt.page, "r")
		#PageContent = f.readlines()
		PageContent = rss_api.GetPage(opt.page)
		#PageContent = BeautifulSoup(''.join(PageContent))
		PageContent = news_api.page_parser(PageContent, True)
		PageContent = rss_api.page_compose(PageContent)
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

	rss_api = rss_tool()
	#content = rss_api.GetPage('http://tw.nextmedia.com/applenews/article/art_id/32242785/IssueID/20100119')
	#rss_api.write2file(rss_api.page_compose(news_api.page_parser(content)))

	if opt.debug:
		print('Get [%s]' %news_api.news_lists[rss_api.Ch2UTF8('頭條要聞')][0]['title'])
		PageContent = rss_api.GetPage(news_api.home_url + news_api.news_lists[rss_api.Ch2UTF8('頭條要聞')][0]['href'])
		sys.stdout.write('[Parsing] -> ')
		PageContent = news_api.page_parser(PageContent)
		sys.stdout.write('[Compose] -> ')
		PageContent = rss_api.page_compose(PageContent)
		print('[Write2File]')
		rss_api.write2file(PageContent, 'main_story.html')
	else:
		RssFileName = {
			# rss_api.Ch2UTF8('副刊'):'Supplement',
			# rss_api.Ch2UTF8('體育'):'Sport',
			# rss_api.Ch2UTF8('蘋果國際'):'International',
			# rss_api.Ch2UTF8('娛樂'):'Entertainment',
			# rss_api.Ch2UTF8('財經'):'Finance',
			rss_api.Ch2UTF8('頭條要聞'):'HeadLine',
			# rss_api.Ch2UTF8('地產'):'Estate',
			# rss_api.Ch2UTF8('豪宅與中古'):'LuxSecHouse',
			# rss_api.Ch2UTF8('家居王'):'HouseWorking'
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
				print '%s, not support\n' % (Classify)
				continue
			rss_api.PastHeader(f, str(Classify))
			print '\n------------- ' + Classify + ' -------------'
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
					print '【' + subClassify + '】' + news_item['title']
					summary = []
					news_api.page_parser(PageContent)
					# summary.append(rss_api.page_compose(news_api.page_parser(PageContent)))
					#summary = [s for s in summary if s != None]
					rss_api.PastEntry(f, news_item['title'], news_api.home_url + news_item['href'], ''.join(summary), subClassify)
					sleep(1)
					#print ''.join(summary)
			rss_api.PastTail(f)
			f.close()

