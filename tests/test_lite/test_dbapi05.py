import numpy
import pytest


@pytest.mark.skipif(True, reason="monetdblite compatibl but: not supported yet")
class TestDescription(object):
    def test_description(self, monetdbe_cursor):
        monetdbe_cursor.execute('select * from sys.tables')
        assert monetdbe_cursor.description is not None

    def test_description_fields(self, monetdbe_cursor):
        monetdbe_cursor.execute('select name from sys.tables')
        assert monetdbe_cursor.description[0][0] == "name"
        assert monetdbe_cursor.description[0][1] == numpy.dtype('O')
