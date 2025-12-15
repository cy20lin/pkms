import unittest

class Test(unittest.TestCase):
    def test_sanity(self):
        expect = 1+1
        actual = 2
        self.assertEqual(expect, actual)

if __name__ == '__main__':
    unittest.main()