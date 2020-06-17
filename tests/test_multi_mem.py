"""
For now we can't handle multiple in-memory databases simultaniously. An error should be raised when someone
tries to open multiple in memory databases.
"""
from tempfile import TemporaryDirectory
from unittest import TestCase, skip

from monetdbe import connect, OperationalError


@skip("If enabled makes the whole test suite fail. ")
class TestMultipleInmemory(TestCase):
    def test_multi_in_mem(self):
        try:
            con1 = connect(":memory:")
            with self.assertRaises(OperationalError):
                con2 = connect(":memory:")
        except Exception:
            del con1
            try:
                del con2
            except UnboundLocalError:
                ...
            raise

    def test_one_mem_one_filesystem(self):

        try:
            loc1 = TemporaryDirectory().name
            con1 = connect(loc1)
            con2 = connect(":memory:")
        except Exception:
            del con1
            del con2
            raise
