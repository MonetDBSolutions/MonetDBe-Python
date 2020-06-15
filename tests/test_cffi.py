import unittest
from monetdbe._lowlevel import lib


class TestCffi(unittest.TestCase):
    def test_cffi(self):
        self.assertEqual(lib.monetdbe_float, 7)
