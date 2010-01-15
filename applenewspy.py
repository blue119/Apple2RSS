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
		f.write('<update>' + strftime("%a, %d %b %Y %H:%M:%S +0800", gmtime()) + '</update>\n')

	def PastTail(self, f):
		f.write('\n')
		f.write('</channel>\n')
		f.write('</rss>\n')

	def PastEntry(self, f, title, link, summary, classify):
		f.write('\n')
		f.write('<item>\n')
		f.write('<title><![CDATA[【' + classify + '】' + title + ']]></title>\n')
		f.write('<pubDate>' + strftime("%a, %d %b %Y %H:%M:%S +0800", gmtime()) + '</pubDate>\n')
		#f.write('<author><![CDATA[' + subclassify +']]></author>\n')
		#f.write('<link><![CDATA[' + link + ']]></link>\n')
		f.write('<description><![CDATA[' + summary + ']]></description>\n')
		f.write('</item>\n')

	def Creatimg_table(self, SmallIMG = '', BigIMG = '', titleIMG = ''):
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

	def write2file(self, b, filename = 'a.html'):
		file_path = '/tmp/' + filename
		f = open(file_path, 'w')
		for i in range((len(b) / 1024) + 1):
			if((len(b) - i * 1024) > 1024):
				f.write(b[i*1024:((i+1)*1024)])
			else:
				f.write(b[i*1024:])
		f.close()

	def GetTitle(PageContent):
		p = re.compile('^<title>(.*)\ \|\ .*\ \|\ .*\ \|.*\|.*</title>')
		Title = p.findall(str(PageContent.title).replace('\n', ''))
		try:
			return Title[0]
		except IndexError:
			print 'Can not parsing this title : "' + str(PageContent.title) + '"'
			Title = None
			return Title

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
			print '<<<' + ClassifyName + '>>>'

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

	def page_parser(self, page_content):
		img_table = []
		summary = []
		page_content = page_content.find('div', {'id':'article_left'})

		# some page have no tag for page_content
		if page_content is None:
			page_content = page_content

		try:
			img = str(page_content.find('script', {'language':'javascript'}))
			p = re.compile('g_ImageTable.*\"(.*)\",\ \"(.*)\",.*javascript:.*\(\'(.*)\',\'http.*\',\'.*\',\'.*\)\"\)')
			result = p.findall(IMG)
			for SmallIMG,titleIMG,BigIMG in result:
				img_table.append(Creatimg_table(SmallIMG, BigIMG, titleIMG))
			summary.append(''.join(img_table))
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
						summary.append(Creatimg_table(Small, Large, Alt))
				else:
					Large, Small, Alt = photo_parse.findall(Photo)[0]
					if '640pix' not in Large:
						Large, Small, Alt = photo_parse2.findall(Photo)[0]
					summary.append(Creatimg_table(Small, Large, Alt))
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
		#print ''.join(summary)
		return ''.join(summary)


if __name__ == '__main__':
	RssFileName = {Ch2UTF8('副刊'):'Supplement', Ch2UTF8('體育'):'Sport', Ch2UTF8('蘋果國際'):'International', 
		Ch2UTF8('娛樂'):'Entertainment', Ch2UTF8('財經'):'Finance', Ch2UTF8('頭條要聞'):'HeadLine', Ch2UTF8('地產王'):'Estate'}

	#NewsChunksDict debug
	#for ClassifyName in NewsChunksDict:
	#	print '------------- ' + ClassifyName + ' -------------'
	#	for NewsList in NewsChunksDict[ClassifyName]:
	#		print '【' + NewsList['subClassify'] + '】' + NewsList['Title'] + NewsList['HREF']
	for Classify in NewsChunksDict:
		try:
			f = open(RssFileName[Classify] + '_RSS.html', 'w')
		except KeyError:
			print '%s, not support\n' % (Classify)
			continue
		PastHeader(f, str(Classify))
		print '\n------------- ' + Classify + ' -------------'
		for NewsList in NewsChunksDict[Classify]:
			try:
				PageContent = GetPage(HomeUrl + NewsList['href'])
			except IOError:
				#try again
				try:
					PageContent = GetPage(HomeUrl + NewsList['href'])
				except IOError:
					#abandent
					continue
			print '【' + NewsList['subClassify'] + '】' + NewsList['title']
			summary = []
			summary.append(PageSorting(PageContent, True))
			summary = [s for s in summary if s != None]
			PastEntry(f, NewsList['title'], HomeUrl + NewsList['href'], ''.join(summary), NewsList['subClassify'])
			sleep(1)
			#print ''.join(summary)
		PastTail(f)
		f.close()

