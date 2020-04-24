import unittest
from _monetdbe_cffi import lib


class TestCffi(unittest.TestCase):
    def test_cffi(self):
        self.assertEqual(lib.monetdb_float, 5)
