from unittest import TestCase
from monetdbe.inter.cffi import CFFIInterAPI



class TestCFFIInterAPI(TestCase):

    def setUp(self) -> None:
        self.inter = CFFIInterAPI()

    def test_startup(self):
        self.inter.startup()

