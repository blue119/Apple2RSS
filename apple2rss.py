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
	RssFileName = {Ch2UTF8('副刊'):'Supplement', Ch2UTF8('體育'):'Sport', 
		Ch2UTF8('蘋果國際'):'International', Ch2UTF8('娛樂'):'Entertainment', 
		Ch2UTF8('財經'):'Finance', Ch2UTF8('頭條要聞'):'HeadLine', 
		Ch2UTF8('地產王'):'Estate'}

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

