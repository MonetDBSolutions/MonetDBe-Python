import unittest

from monetdbe.inter.cffi import CFFIInterAPI


class MyTestCase(unittest.TestCase):
    def setUp(self) -> None:
        inter = CFFIInterAPI()

    def test_something(self):
        self.assertEqual(True, False)


if __name__ == '__main__':
    unittest.main()
