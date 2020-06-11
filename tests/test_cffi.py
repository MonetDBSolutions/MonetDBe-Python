import unittest
from monetdbe._lowlevel import lib


class TestCffi(unittest.TestCase):
    def test_cffi(self):
        self.assertEqual(lib.monetdb_float, 7)
