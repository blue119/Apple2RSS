import unittest

a = ['aaaaa', 'bbbbb', 'ccccc']
b = ['aaaaa', 'bbbbb', 'ccccc']

class MainTestCase(unittest.TestCase):
	def setUp(self):
		pass

	def tearDown(self):
		pass

	def testAMethod(self):
		self.assertTrue(True)
		self.assertEqual(a, b)

if __name__ == "__main__":
	unittest.main()

