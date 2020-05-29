import numpy
import pandas
import pytest


class TestSimpleDBAPI:
    def test_regular_selection(self, monetdbe_cursor):
        monetdbe_cursor.execute('SELECT * FROM integers')
        result = monetdbe_cursor.fetchall()
        assert result == [(0,), (1,), (2,), (3,), (4,), (5,), (6,), (7,), (8,), (9,), (None,)], "Incorrect result returned"

    def test_numpy_selection(self, monetdbe_cursor):
        monetdbe_cursor.execute('SELECT * FROM integers')
        result = monetdbe_cursor.fetchnumpy()
        arr = numpy.ma.masked_array(numpy.arange(11))
        arr.mask = [False] * 10 + [True]
        numpy.testing.assert_array_equal(result['i'], arr, "Incorrect result returned")

    def test_pandas_selection(self, monetdbe_cursor):
        monetdbe_cursor.execute('SELECT * FROM integers')
        result = monetdbe_cursor.fetchdf()
        arr = numpy.ma.masked_array(numpy.arange(11))
        arr.mask = [False] * 10 + [True]
        arr = {'i': arr}
        arr = pandas.DataFrame.from_dict(arr)
        # assert str(result) == str(arr), "Incorrect result returned"
        pandas.testing.assert_frame_equal(result, arr)

    def test_numpy_creation(self, monetdbe_cursor):
        # numpyarray = {'i': numpy.arange(10), 'v': numpy.random.randint(100, size=(1, 10))}  # segfaults
        data_dict = {'i': numpy.arange(10), 'v': numpy.random.randint(100, size=10)}
        monetdbe_cursor.create('numpy_creation', data_dict)
        monetdbe_cursor.commit()

        monetdbe_cursor.execute('SELECT * FROM numpy_creation')
        result = monetdbe_cursor.fetchnumpy()

        numpy.testing.assert_array_equal(result['i'], data_dict['i'])
        numpy.testing.assert_array_equal(result['v'], data_dict['v'])

    def test_pandas_creation(self, monetdbe_cursor):
        data_dict = {'i': numpy.arange(10), 'v': numpy.random.randint(100, size=10)}
        dframe = pandas.DataFrame.from_dict(data_dict)
        monetdbe_cursor.create('dframe_creation', dframe)

        monetdbe_cursor.execute('SELECT * FROM dframe_creation')
        result = monetdbe_cursor.fetchnumpy()

        numpy.testing.assert_array_equal(result['i'], data_dict['i'])
        numpy.testing.assert_array_equal(result['v'], data_dict['v'])

    def test_numpy_insertion(self, monetdbe_cursor):
        data_dict = {'i': numpy.arange(10), 'v': numpy.random.randint(100, size=10)}
        monetdbe_cursor.execute("CREATE TABLE numpy_insertion (i INT, v INT)")
        monetdbe_cursor.insert('numpy_insertion', data_dict)
        monetdbe_cursor.commit()

        monetdbe_cursor.execute("SELECT * FROM numpy_insertion")
        result = monetdbe_cursor.fetchnumpy()

        numpy.testing.assert_array_equal(result['i'], data_dict['i'])
        numpy.testing.assert_array_equal(result['v'], data_dict['v'])

    def test_pandas_insertion(self, monetdbe_cursor):
        data_dict = {'i': numpy.arange(10), 'v': numpy.random.randint(100, size=10)}
        dframe = pandas.DataFrame.from_dict(data_dict)
        monetdbe_cursor.execute("CREATE TABLE pandas_insertion (i INT, v INT)")
        monetdbe_cursor.insert('pandas_insertion', dframe)
        monetdbe_cursor.commit()

        monetdbe_cursor.execute("SELECT * FROM pandas_insertion")
        result = monetdbe_cursor.fetchnumpy()

        numpy.testing.assert_array_equal(result['i'], data_dict['i'])
        numpy.testing.assert_array_equal(result['v'], data_dict['v'])

    def test_masked_array_insertion(self, monetdbe_cursor):
        data_dict = {'i': numpy.ma.masked_array(numpy.arange(10), mask=([False] * 9 + [True]))}
        monetdbe_cursor.execute("CREATE TABLE masked_array_insertion (i INT)")
        monetdbe_cursor.insert("masked_array_insertion", data_dict)
        monetdbe_cursor.commit()

        monetdbe_cursor.execute("SELECT * FROM masked_array_insertion")
        result = monetdbe_cursor.fetchnumpy()

        numpy.testing.assert_array_equal(result['i'], data_dict['i'])
