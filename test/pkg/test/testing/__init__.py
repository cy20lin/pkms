import unittest
import os.path
import os
from testing import PROJECT_DIR

class Test(unittest.TestCase):
    def test_project_dir(self):
        expect = os.path.normpath(os.path.join(os.path.dirname(__file__), *['..']*4)).lower()
        actual = PROJECT_DIR.lower()
        self.assertEqual(expect, actual)

if __name__ == '__main__':
    unittest.main()