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

	def CreatImgTable(self, SmallIMG = '', BigIMG = '', titleIMG = ''):
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
		rss = []
		for i in content:
			if type(i) is type([]):
				rss.append(self.CreatImgTable(SmallIMG = i[0], BigIMG = i[1], titleIMG = i[2]))
			else:
				rss.append(i)
		return ''.join(rss)

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

if __name__ == '__main__':
	from applenewsapi import apple_news_api
	kk = apple_news_api()
	kk.get_list()
	#kk.show_news_list()

	rss = rss_tool()
	#content = rss.GetPage('http://tw.nextmedia.com/applenews/article/art_id/32242785/IssueID/20100119')
	#rss.write2file(rss.page_compose(kk.page_parser(content)))

	RssFileName = {rss.Ch2UTF8('副刊'):'Supplement', rss.Ch2UTF8('體育'):'Sport', 
		rss.Ch2UTF8('蘋果國際'):'International', rss.Ch2UTF8('娛樂'):'Entertainment', 
		rss.Ch2UTF8('財經'):'Finance', rss.Ch2UTF8('頭條要聞'):'HeadLine', 
		rss.Ch2UTF8('地產王'):'Estate'}

	#NewsChunksDict debug
	#for ClassifyName in NewsChunksDict:
	#	print '------------- ' + ClassifyName + ' -------------'
	#	for NewsList in NewsChunksDict[ClassifyName]:
	#		print '【' + NewsList['subClassify'] + '】' + NewsList['Title'] + NewsList['HREF']
	PageContent = []
	for Classify in kk.news_list:
		try:
			f = open(RssFileName[Classify] + '_RSS.html', 'w')
		except KeyError:
			print '%s, not support\n' % (Classify)
			continue
		rss.PastHeader(f, str(Classify))
		print '\n------------- ' + Classify + ' -------------'
		for NewsList in kk.news_list[Classify]:
			try:
				PageContent = rss.GetPage(kk.home_url + NewsList['href'])
			except IOError:
				#try again
				try:
					PageContent = rss.GetPage(kk.home_url + NewsList['href'])
				except IOError:
					#abandent
					continue
			print '【' + NewsList['subClassify'] + '】' + NewsList['title']
			summary = []
			summary.append(rss.page_compose(kk.page_parser(PageContent)))
			#summary = [s for s in summary if s != None]
			rss.PastEntry(f, NewsList['title'], kk.home_url + NewsList['href'], ''.join(summary), NewsList['subClassify'])
			sleep(1)
			#print ''.join(summary)
		rss.PastTail(f)
		f.close()

