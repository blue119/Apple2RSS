#!/usr/bin/python
# -*- coding: utf8 -*-

from urllib import urlopen
from time import gmtime, strftime, sleep
import sys, re, copy, os
import urllib2
import shutil

reload(sys)
sys.path.append(os.path.dirname(os.path.realpath(__file__ + '/../')))
#sys.path.insert(0, '../')
sys.setdefaultencoding('utf8')
from BeautifulSoup import BeautifulSoup

# http://stackoverflow.com/questions/273192/python-best-way-to-create-directory-if-it-doesnt-exist-for-file-write
# http://www.penzilla.net/tutorials/python/fileio/


def Ch2UTF8(char):
    return unicode(char, 'utf-8', 'ignore')

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


def write2file(filename, contents):
	f = open(filename, 'w')
	for i in range((len(contents) / 1024) + 1):
		if((len(contents) - i * 1024) > 1024):
			f.write(contents[i*1024:((i+1)*1024)])
		else:
			f.write(contents[i*1024:])
	f.close()

HomeUrl = 'http://tw.nextmedia.com/'
AppleNewHome = urlopen( HomeUrl + 'applenews/todayapple').read()
#AppleNewHome = unicode(AppleNewHome, 'big5', 'ignore')
#f = open('todayapple', 'r')
#AppleNewHome =  f.read()
#f.close()

soupAppleNewHome = BeautifulSoup(AppleNewHome)

RssFileName = {Ch2UTF8('副刊'):'Supplement', Ch2UTF8('體育'):'Sport',
    Ch2UTF8('蘋果國際'):'International', Ch2UTF8('娛樂'):'Entertainment',
    Ch2UTF8('財經'):'Finance', Ch2UTF8('頭條要聞'):'HeadLine',
    Ch2UTF8('地產王'):'Estate'}

Contents = [] 
Item = {}   
NewsChunksDict = {}

ClassifySector = soupAppleNewHome.findAll('div', {'id':'nl_box'})
for i in range(len(ClassifySector)):
    ClassifyName = ClassifySector[i].find('span', {'class':'nl_unit_bar_title'}).string
    #print ClassifyName
    for j in range(len(ClassifySector[i].findAll('span', {'class':'nl_unit_second_title'}))):
        subClassifyName = ClassifySector[i].findAll('span', {'class':'nl_unit_second_title'})[j].string
        #print subClassifyName
        for k in ClassifySector[i].findAll('div', {'id':'nl_unitlist'})[j].findAll('a'):
            #print '[%s] %s : %s' %(subClassifyName, k.string, k['href'])
            Item['subClassify'] = str(subClassifyName)
            Item['title'] = str(k.string)
            Item['href'] = str(k['href'])
            Contents.append(copy.copy(Item))
    NewsChunksDict[ClassifyName] = copy.copy(Contents)
    Contents = []

path_name = os.path.basename(NewsChunksDict[Ch2UTF8('頭條要聞')][0]['href'])

# Check folder
if os.path.exists(path_name):
	try:
		print 'Duplicate: delete older file'
		os.rmdir(path_name)
	except OSError:
		shutil.rmtree(path_name)

os.makedirs(path_name)

p = re.compile('^.*art_id/([0-9]+)/.*$')
basename = ''
#/applenews/article/art_id/32242763/IssueID/20100119
for Classify in NewsChunksDict:
	print '<<< ' + Classify + ' >>>'
	for NewsList in NewsChunksDict[Classify]:
		basename = p.findall(NewsList['href'])[0] + '.html'
		full_path = path_name + '/' + basename
		print '【' + NewsList['subClassify'] + '】' + NewsList['title'] + ' ---> ' + full_path
		web_page = GetPage( HomeUrl + NewsList['href'])
		write2file(full_path, str(web_page))
#	f = open(RssFileName[Classify] + '_RSS.html', 'w')


