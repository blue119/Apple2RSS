from urllib import urlopen
import sys, re
import urllib2
import logging
from shutil import rmtree
import os

logger = logging.getLogger('apple2rss.utils')

class utils(object):
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
        try:
            page_redirect = BeautifulSoup(html_page).find('script').string
            if page_redirect is not None:
                redirect_p = re.compile('[/W]+(.*)\"')
                redirect_url = redirect_p.findall(page_redirect)[0]
                logger.info('page redirect to %s', redirect_url)
                if 'http' not in redirect_url:
                    redirect_url = self.home_url + redirect_url
                return self.GetPage(redirect_url)
        except:
            pass

        return html_page

    def Url2TinyUrl(self, URL):
        return urlopen('http://tinyurl.com/api-create.php?url=' + URL).read()

    @staticmethod
    def Ch2UTF8(char):
        return unicode(char, 'utf-8', 'ignore')

    @staticmethod
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

    def write2file(self, content, file_path = '/tmp/a.html'):
        f = open(file_path, 'w')
        for i in range((len(content) / 1024) + 1):
            if((len(content) - i * 1024) > 1024):
                f.write(content[i*1024:((i+1)*1024)])
            else:
                f.write(content[i*1024:])
        f.close()
