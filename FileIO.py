import urllib2
import httplib

class FileIOBase(object):
	"""docstring for FileIOBase"""
	def __init__(self):
		super(FileIOBase, self).__init__()
		pass

	def open(self):
		"""docstring for open"""
		raise NotImplementedError

	def read(self):
		"""docstring for read"""
		raise NotImplementedError

	def delete(self):
		"""docstring for delete"""
		raise NotImplementedError
		self._content = None

	def write(self):
		"""docstring for write"""
		raise NotImplementedError

class RemoteHtmlFileIO(FileIOBase):
	"""HtmlFileIO's open function is grab a page from web site return str"""
	def __init__(self, url = None):
		super(RemoteHtmlFileIO, self).__init__()
		self._url = url
		self._content = None

	@property
	def url(self):
		return self._url

	def open(self, url = None):
		"""docstring for open"""
		if url:
			self._url = url

		try:
			url_req = urllib2.Request(self._url)
			url_req.add_header("User-agent", "Mozilla/5.0")
			self._content = urllib2.urlopen(url_req).read()
		except IOError, ErrMsg:
			logger.warning('Maybe %s is dead', URL)
			return None
		except httplib.BadStatusLine:
			logger.warning('happen BadStatusLine', URL)
			return None

		return self._content

	def read(self):
		"""docstring for read"""
		return self._content

	def delete(self):
		"""docstring for delete"""
		self._content = None

