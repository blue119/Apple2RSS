#!/usr/bin/python
# -*- coding: utf8 -*-

#v0.1 can be run but not is good.

from urllib import urlopen
from BeautifulSoup import BeautifulSoup
from time import gmtime, strftime, sleep
import sys, re, copy

reload(sys)
sys.setdefaultencoding('utf8')

def PastHeader(f, classify):
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

def PastTail(f):
	f.write('\n')
	f.write('</channel>\n')
	f.write('</rss>\n')

def PastEntry(f, title, link, summary, classify):
	f.write('\n')
	f.write('<item>\n')
	f.write('<title><![CDATA[【' + classify + '】' + title + ']]></title>\n')
	f.write('<pubDate>' + strftime("%a, %d %b %Y %H:%M:%S +0800", gmtime()) + '</pubDate>\n')
	#f.write('<author><![CDATA[' + subclassify +']]></author>\n')
	#f.write('<link><![CDATA[' + link + ']]></link>\n')
	f.write('<description><![CDATA[' + summary + ']]></description>\n')
	f.write('</item>\n')

def CreatImgTable(SmallIMG = '', BigIMG = '', titleIMG = ''):
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

def GetPage(URL):
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

def Url2TinyUrl(URL):
	return urlopen('http://tinyurl.com/api-create.php?url=' + URL).read()

def Ch2UTF8(char):
	return unicode(char, 'utf-8', 'ignore')

def PageSorting(PageContent, First = False):
	ImgTable = []
	summary = []
	Content = PageContent.find('div', {'id':'article_left'})
	try:
		IMG = str(Content.find('script', {'language':'javascript'}))
		p = re.compile('g_ImageTable.*\"(.*)\",\ \"(.*)\",.*javascript:.*\(\'(.*)\',\'http.*\',\'.*\',\'.*\)\"\)')
		result = p.findall(IMG)
		for SmallIMG,titleIMG,BigIMG in result:
			ImgTable.append(CreatImgTable(SmallIMG, BigIMG, titleIMG))
		summary.append(''.join(ImgTable))
	except AttributeError: #No Picture in intro
		pass

	#Grab alticl section
	p = re.compile('.*iclickAdBody_Start\"\>\<\/span\>(.*)\<span\ name\=\"iclickAdBody_End\"\ id\=.*')
	Content = BeautifulSoup(p.findall(str(Content).replace('\n',''))[0])

	#Abstract
	summary.append(str(Content.find('p', {'class':'summary'})))
	
	tmp = str(Content).split('<h2 class="article_title">')
	#remove Abstract
	if 'summary' in tmp[0]:
		del tmp[0]

	#First Paragraph
	tmpArray = []
	tmpArray2 = []
	tmpArray3 = []
	p = re.compile('.*<h2>(.*)</h2>(.*)')
	tmp = str(Content).split('<br /></p><div class="spacer"></div>')
	for i in tmp:
		if p.findall(i):
			tmpArray.append(p.findall(i)[0])
	for i, j in tmpArray:
	  	tmpArray2.append('<div id="block"><h3>%s</h3>%s</div>'%(i, j))
	paragraph  = BeautifulSoup(''.join(tmpArray2))
	p = re.compile('.*imageUrl=(.*)\"\ title=\"(.*)\"\ target.*img src=\"(.*)\"\ alt=\".*')
	for i in paragraph.findAll('div', {'id':'block'}):
		tmpArray3.append(str(i.h3))
		result = p.findall(str(i)) # <= have picture
		if result:
			for BigIMG, titleIMG, SmallIMG in result:
				ImgTable = []
				ImgTable.append(CreatImgTable(SmallIMG, BigIMG, titleIMG))
				tmpArray3.append(''.join(ImgTable))
		tmpArray3.append(str(i.find('p', {'class':'paragraph'})).replace('<p class=\"paragraph\">', '').replace('</p>', ''))
#	summary = summary + ''.join(tmpArray3)
	summary.append(''.join(tmpArray3))
	#print summary
#	return summary
	return ''.join(summary)

def GetTitle(PageContent):
	p = re.compile('^<title>(.*)\ \|\ .*\ \|\ .*\ \|.*\|.*</title>')
	Title = p.findall(str(PageContent.title).replace('\n', ''))
	try:
		return Title[0]
	except IndexError:
		print 'Can not parsing this title : "' + str(PageContent.title) + '"'
		Title = None
		return Title

HomeUrl = 'http://tw.nextmedia.com/'
AppleNewHome = urlopen( HomeUrl + 'applenews/todayapple').read()
#AppleNewHome = unicode(AppleNewHome, 'big5', 'ignore')
soupAppleNewHome = BeautifulSoup(AppleNewHome)

RssFileName = {Ch2UTF8('副刊'):'Supplement', Ch2UTF8('體育'):'Sport', 
	Ch2UTF8('蘋果國際'):'International', Ch2UTF8('娛樂'):'Entertainment', 
	Ch2UTF8('財經'):'Finance', Ch2UTF8('頭條要聞'):'HeadLine', 
	Ch2UTF8('地產王'):'Estate'}

Contents = []
Item = {}	
NewsChunksDict = {}

# <div id="nl_box"> <- Title Item
# <span class="nl_unit_bar_title">頭條要聞</span> <- Classify
# <span class="nl_unit_second_title">頭條</span> <-  subClassify
# <div id="nl_unitlist"> <= subClassify link

ClassifySector = soupAppleNewHome.findAll('div', {'id':'nl_box'})
for i in range(len(ClassifySector)):
	ClassifyName = ClassifySector[i].find('span', {'class':'nl_unit_bar_title'}).string
	print ClassifyName
	for j in range(len(ClassifySector[i].findAll('span', {'class':'nl_unit_second_title'}))):
		subClassifyName = ClassifySector[i].findAll('span', {'class':'nl_unit_second_title'})[j].string
		print subClassifyName
		for k in ClassifySector[i].findAll('div', {'id':'nl_unitlist'})[j].findAll('a'):
			print '[%s] %s : %s' %(subClassifyName, k.string, k['href']) 
			Item['subClassify'] = str(subClassifyName)
			Item['title'] = str(k.string)
			Item['href'] = str(k['href'])
			Contents.append(copy.copy(Item))
	NewsChunksDict[ClassifyName] = copy.copy(Contents)
	Contents = []

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
		#Grab Next Page
		try:
			for NextPage in PageContent.find('div', {'id':'pagebar'}).find('ul', {'class':'number'}).findAll('a'):
				print '\tGetNextPage'
				PageContent = GetPage(NextPage['href'])
				if PageContent is None:
					break
				summary.append(PageSorting(PageContent))
				sleep(1)
		except AttributeError:
			pass
		summary = [s for s in summary if s != None]
		PastEntry(f, NewsList['title'], HomeUrl + NewsList['href'], ''.join(summary), NewsList['subClassify'])
		sleep(2)
		#print ''.join(summary)
	PastTail(f)
	f.close()

