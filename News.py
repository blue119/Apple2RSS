
class NewsBase(object):
	"""docstring for NewsBase"""
	def __init__(self, url):
		super(NewsBase, self).__init__()
		self._url = url

	def getList(self):
		"""docstring for getList"""
		raise NotImplementedError

