import numpy
import pytest


class TestMultipleResultSets:
    def test_regular_selection(self, monetdbe_cursor):
        monetdbe_cursor.execute('SELECT * FROM integers')
        monetdbe_cursor.execute('SELECT * FROM integers')
        result = monetdbe_cursor.fetchall()

        expected = [(i,) for i in range(10)] + [(None,)]
        assert result == expected, "Incorrect result returned"

    def test_numpy_selection(self, monetdbe_cursor):
        monetdbe_cursor.execute('SELECT * FROM integers')
        monetdbe_cursor.execute('SELECT * FROM integers')
        result = monetdbe_cursor.fetchnumpy()
        expected = numpy.ma.masked_array(numpy.arange(11), mask=([False] * 10 + [True]))

        numpy.testing.assert_array_equal(result['i'], expected)
