import numpy
import pytest


@pytest.mark.skipif(True, reason="monetdblite compatibl but: not supported yet")
class TestMultipleResultSets:
    def test_regular_selection(self, monetdbe_cursor):
        monetdbe_cursor.execute('SELECT * FROM integers')
        monetdbe_cursor.execute('SELECT * FROM integers')
        result = monetdbe_cursor.fetchall()
        assert result == [[0], [1], [2], [3], [4], [5], [6], [7], [8], [9], [None]], "Incorrect result returned"

    def test_numpy_selection(self, monetdbe_cursor):
        monetdbe_cursor.execute('SELECT * FROM integers')
        monetdbe_cursor.execute('SELECT * FROM integers')
        result = monetdbe_cursor.fetchnumpy()
        expected = numpy.ma.masked_array(numpy.arange(11), mask=([False] * 10 + [True]))

        numpy.testing.assert_array_equal(result['i'], expected)
