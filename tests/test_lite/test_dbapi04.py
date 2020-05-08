import pytest


@pytest.mark.skipif(True, reason="monetdblite compatibl but: not supported yet")
class TestSimpleDBAPI:
    def test_regular_selection(self, monetdbe_cursor):
        monetdbe_cursor.execute('SELECT * FROM integers')
        result = monetdbe_cursor.fetchall()
        assert result == [[0], [1], [2], [3], [4], [5], [6], [7], [8], [9], [None]], "Incorrect result returned"
