#!/usr/bin/python
# -*- coding: utf8 -*-

from FileIO import RemoteHtmlFileIO as html_r
from utils import utils
from urllib import urlopen
from BeautifulSoup import BeautifulSoup
from time import gmtime, strftime, sleep, localtime, time
from copy import copy
from applenewsapi import AppleNews
from socket import setdefaulttimeout
from shutil import rmtree
import sys, re
import urllib2
import optparse
import os
import logging
import traceback

reload(sys)
sys.setdefaultencoding('utf8')

LOG_FILENAME = 'logs/apple2rss_%s.log' % (strftime("%Y_%m_%d_%H_%M_%S", localtime()))
logging.basicConfig(
	# filename = LOG_FILENAME,
	level=logging.DEBUG, filemode = 'a',
	datefmt = '%Y-%m-%d %H:%M:%S',
	format='%(asctime)s : %(name)s : %(levelname)s\t%(message)s')

logger = logging.getLogger('apple2rss.main')


class SaveAppleNewsToHtml(object):
	def __init__(self, prefix_url):
		self.logger = logging.getLogger(self.__class__.__name__)
		self.home_url = prefix_url
		self.store_in = ''

	def PastHeader(self, f, classify):
		f.write('<html>\n')
		f.write('\t<head>\n')
		f.write('\t\t<title>' + classify + strftime("%a, %d %b %Y %H:%M:%S") + '</title>\n')
		f.write('\t\t<meta http-equiv="Content-Type" content="text/html; charset=utf-8">\n')
		f.write('\t\t<style type="text/css" media="all">\n')
		f.write('\t\t\t#border {\n')
		f.write('\t\t\t\tborder: 1px dashed #ccc;\n')
		f.write('\t\t\t}\n')
		f.write('\t\t</style>\n')
		f.write('\t</head>\n')
		f.write('\t<body>\n')
		f.write('\n')

	def PastTail(self, f):
		f.write('\n')
		f.write('\t</body>\n')
		f.write('</html>\n')

	def PastEntry(self, f, title, link, summary, classify):
		f.write('\t\t<b>【' + classify + '】' + title + '</b>\n')
		f.write('\t\t<p id="border">\n')
		f.write('\t\t\t' +  summary + '\n')
		f.write('\t\t</p>\n')

	def _photo_dl_save(self, url):
		file_name = re.compile('.*\/([\w\.\-]+[jpg|JPG])$').findall(url)[0]
		f = urlopen(url)
		local_file = open(self.store_in + '/img/' + file_name, "w")
		local_file.write(f.read())
		local_file.close()
		return file_name

	def _video_dl_save(self, url):
		print "download action news: " + url
		file_name = re.compile('.*\/([\w\.\-]+[mp4])$').findall(url)[0]
		f = urlopen(url)
		local_file = open(self.store_in + '/img/' + file_name, "w")
		local_file.write(f.read())
		local_file.close()
		return file_name

	def _img_table(self, photo, img_dl=True):
		''' if the img_dl is true, it will download image and replace url to local site.
		'''
		Title = photo.get('title')
		if img_dl:
			#FIXME
			if photo.get('small') == '':
				Small = ''
			else:
				Small = 'img/' + self._photo_dl_save(photo.get('small'))

			if photo.get('big') == '':
				Big = ''
			else:
				Big = 'img/' + self._photo_dl_save(photo.get('big'))
		else:
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

		slide_photo = content.get('slide_photo')

		# h1 and h2
		if content['h2']:
			compose.append('<b>' + content['h2'] + '</b><br />')

		# the content may have no picture in summary.
		if content.get('an_photo'):
			compose.append("<a href=\"img/" + \
				self._video_dl_save(content.get('an_video')) + "\">" + \
				"<img width=\"460\" src=\"img/" + \
				self._photo_dl_save(content.get('an_photo').get('small'))  + \
				"\"/></a><br />")

		if content.get('article'):
			for article in content.get('article'):
				compose.append('<br /><b>' + article['header'] + '</b><br />')
				if len(slide_photo):
					compose.append(self._img_table(slide_photo[0]))
					slide_photo = slide_photo[1:]
				compose.append(article['text'].replace('\n', '<br />'))

		for i in slide_photo:
			compose.append(self._img_table(i))

		return ''.join(compose)

def main_argv_parser(argv):
	opt_dic = {}
	option_parser = optparse.OptionParser(usage=__USAGE__, version=__version__)
	option_parser.disable_interspersed_args()

	option_parser.add_option("-S", "--save", action="store_true", dest="save",
		help=("like as -D, not only download the news page, but also do transform."))
	option_parser.add_option("-D", "--download", action="store_true", dest="only_dl",
		help=("only to download news page don't transform to rss format."))
	option_parser.add_option("-f", "--folder", action="store", type="string",
		dest="folder", default="public_html", help=("Slecte a folder, store in.\n"
		"If it's not exist will be create. default is \"public_html\""))
	option_parser.add_option("-p", "--page", action="store", dest="page", type="string",
		help=("Download and Coverte this PAGE, then save to one_page/apple.html.\n"))

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
			rmtree(path)
			logger.info("create: %s",  path)
			os.mkdir(path)
	else:
		logger.info("create: %s",  path)
		os.mkdir(path)

def get_one_page(utils):
	time_one_page = time()
	news_api = AppleNews(html_r(), 'http://www.appledaily.com.tw/')
	api = SaveAppleNewsToHtml(news_api.home_url)
	api.store_in = "one_page/"
	mkdir(api.store_in, True)
	mkdir(api.store_in + '/img', True)
	f = open(api.store_in + 'apple.html', 'w')

	PageContent = utils.GetPage(opt.page)
	PageContent = news_api.page_parser(PageContent)
	api.PastHeader(f, "")
	PageContent = api.page_compose(PageContent)
	api.PastEntry(f, "", "", ''.join(PageContent), "")
	api.PastTail(f)
	logger.info("get one page spend %d sec", time() - time_one_page)
	sys.exit()

__version__ = "apple2rss Ver:0.0.1"
__author__ = "Yao-Po Wang (blue119@gmail.com)"
__USAGE__ = "usage: python %prog"

if __name__ == '__main__':
	time_start = time()
	opt = main_argv_parser(sys.argv)
	utils = utils()

	# some connection timeout in seconds
	timeout = 10
	setdefaulttimeout(timeout)

	if opt.page:
		get_one_page(utils)

	time_get_list = time()
	news_api = AppleNews(html_r(), 'http://www.appledaily.com.tw/')
	news_api.get_list('appledaily/todayapple')
	time_end_get_list = time() - time_get_list
	logger.info("get list spend %d sec", time_end_get_list)

	api = SaveAppleNewsToHtml(news_api.home_url)

	#Folder Prepare
	api.store_in = opt.folder + "/" + strftime("%Y-%m-%d", localtime())
	mkdir(opt.folder, False)
	mkdir(api.store_in, False)
	mkdir(api.store_in + '/img', False)

	NameMap = {
		utils.Ch2UTF8('頭條要聞'):'HeadLine',
		utils.Ch2UTF8('副刊'):'Supplement',
		utils.Ch2UTF8('體育'):'Sport',
		utils.Ch2UTF8('蘋果國際'):'International',
		utils.Ch2UTF8('娛樂'):'Entertainment',
		utils.Ch2UTF8('財經'):'Finance',
		utils.Ch2UTF8('地產'):'Estate',
		utils.Ch2UTF8('豪宅與中古'):'LuxSecHouse',
		utils.Ch2UTF8('家居王'):'HouseWorking',
		utils.Ch2UTF8('論壇與專欄'):'Column'
	}

	for Classify in news_api.news_lists:
		if NameMap.get(Classify):
			f = open(api.store_in + "/" + NameMap.get(Classify) + '_RSS.html', 'w')
		else:
			logger.info('%s, not support' % (Classify))
			continue

		api.PastHeader(f, str(Classify))
		logger.info('------------- %s -------------', Classify)

		for subClassify in news_api.news_lists[Classify]:
			for NewsList in news_api.news_lists[Classify][subClassify]:
				# print subClassify
				time_start_item = time()
				try:
					page = news_api.get_page(news_api.home_url + NewsList['href'])
				except IOError:
					#abandent
					logger.info('The item spend %d secs' % (time() - time_start_item))
					continue

				logger.info('【' + subClassify + '】' + NewsList['title'])
				summary = []

				try:
					result =  news_api.page_parser(page)
				except:
					logger.critical('parse failur %s%s', news_api.home_url, NewsList['href'])
					traceback.print_exc(file=sys.stdout)
					logger.info('The item spend %d secs' % (time() - time_start_item))
					continue

				try:
					summary.append(api.page_compose(result))
				except:
					logger.critical('compose failur %s%s', news_api.home_url, NewsList['href'])
					logger.critical('Dump:')
					logger.critical(str(result))
					traceback.print_exc(file=sys.stdout)
					logger.info('The item spend %d secs' % (time() - time_start_item))
					continue

				summary = [s for s in summary if s != None]
				api.PastEntry(f, NewsList['title'], news_api.home_url + NewsList['href'], ''.join(summary), subClassify)
				logger.info('The item spend %d secs' % (time() - time_start_item))
				sleep(1)
				#print ''.join(summary)
		api.PastTail(f)
		logger.info('The total jobs spend %d secs' % (time() - time_start))
		f.close()

