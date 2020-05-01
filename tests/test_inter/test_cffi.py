from unittest import TestCase
from monetdbe._cffi import MonetEmbedded


class TestCFFIInterAPI(TestCase):

    def setUp(self) -> None:
        self.inter = MonetEmbedded()

    def test_startup(self):
        self.inter.startup()

