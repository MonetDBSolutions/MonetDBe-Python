from unittest import TestCase

import numpy
import pandas as pd
import pytest

import monetdbe


class TestmonetdbeBase(TestCase):
    def setUp(self) -> None:
        self.con = monetdbe.connect()

    def test_regular_selection(self):
        con = monetdbe.connect()
        monetdbe.sql('CREATE TABLE pylite00 (i INTEGER)', client=con)
        con.execute('INSERT INTO pylite00 VALUES (1), (2), (3), (4), (5)')
        result = con.execute('SELECT * FROM pylite00').fetchdf()
        assert len(result['i']) == 5, "Incorrect result"

    def test_monetdbe_create(self):
        cur = monetdbe.create('pylite01', {'i': numpy.arange(1000)})
        result = monetdbe.sql('select * from pylite01', client=cur.connection)
        assert len(result['i']) == 1000, "Incorrect result"

    def test_monetdbe_insert(self):
        cur = monetdbe.create('pylite02', {'i': numpy.arange(1000)})
        cur.insert('pylite02', {'i': numpy.arange(1000)})
        result = cur.execute('select * from pylite02').fetchdf()
        assert len(result['i']) == 2000, "Incorrect result"

    def test_monetdbe_create_multiple_columns(self):
        arrays = numpy.arange(100000).reshape((5, 20000))
        cur = monetdbe.create('pylite03',
                              {'i': arrays[0], 'j': arrays[1], 'k': arrays[2], 'l': arrays[3], 'm': arrays[4]})
        result = cur.execute('select * from pylite03').fetchnumpy()
        assert len(result) == 5, "Incorrect amount of columns"
        assert len(result['i']) == 20000, "Incorrect amount of rows"

    def test_sql_types(self):
        con = monetdbe.connect()
        cur = con.execute('CREATE TABLE pylite04_decimal(d DECIMAL(18,3))')
        cur.insert('pylite04_decimal', {'d': numpy.arange(100000).astype(numpy.int64)})
        result = cur.execute('SELECT * FROM pylite04_decimal').fetchdf()
        assert result['d'][0] == 0, "Incorrect result"

        cur.execute('CREATE TABLE pylite04_date(d DATE)')
        cur.execute("INSERT INTO pylite04_date VALUES ('2000-01-01')")
        result = cur.execute('SELECT d FROM pylite04_date').fetchdf()
        assert result['d'][0] == pd.Timestamp('2000-01-01'), "Incorrect result"

    def test_connections(self):
        # create two clients
        conn = monetdbe.connect(autocommit=True)
        conn2 = monetdbe.connect()
        # create a table within a transaction in one client
        cur = conn.cursor()
        cur.create('pylite05', {'i': numpy.arange(1000)})

        # check that table was successfully created
        result = monetdbe.sql('SELECT MIN(i) AS minimum FROM pylite05', client=conn)
        assert result['minimum'][0] == 0, "Incorrect result"
        # attempt to query the table from another client
        # with pytest.raises(monetdbe.DatabaseError):
        monetdbe.sql('SELECT * FROM pylite05', client=conn2)

        # now commit the table
        monetdbe.sql('COMMIT', client=conn)
        # query the table again from the other client, this time it should be there
        result = monetdbe.sql('SELECT MIN(i) AS minimum FROM pylite05', client=conn2)
        assert result['minimum'][0] == 0, "Incorrect result"

    def test_non_existent_table(self, ):
        # select from non-existent table
        with pytest.raises(monetdbe.DatabaseError):
            monetdbe.sql('select * from nonexistenttable')

    def test_invalid_connection_object(self):
        # invalid connection object
        with pytest.raises(TypeError):
            monetdbe.sql('select * from tables', client=33)

    def test_invalid_colnames(self):
        # invalid colnames
        with pytest.raises(monetdbe.DatabaseError):
            monetdbe.create('pylite06', {33: []})

    def test_empty_colnames(self):
        # empty colnames
        with pytest.raises(monetdbe.DatabaseError):
            monetdbe.create('pylite07', {'': []})

    def test_invalid_key_dict(self):
        # dictionary with invalid keys
        d = dict()
        d[33] = 44
        with pytest.raises(monetdbe.ProgrammingError):
            monetdbe.create('pylite08', d)

    def test_missing_dict_key(self):
        # missing dict key in insert
        cur = monetdbe.create('pylite09', dict(a=[], b=[], c=[]))
        with pytest.raises(monetdbe.DatabaseError):
            cur.insert('pylite09', dict(a=33, b=44))

    def test_bad_column_number(self):
        # too few columns in insert
        cur = monetdbe.create('pylite10', dict(a=[], b=[], c=[]))
        with pytest.raises(monetdbe.DatabaseError):
            cur.insert('pylite10', {'a': [33], 'b': [44]})

    def test_many_sql_statements(self):
        for i in range(5):  # FIXME 1000
            conn = monetdbe.connect()
            cur = conn.execute('CREATE TABLE pylite11 (i INTEGER)')
            cur.insert('pylite11', {'i': numpy.arange(10).astype(numpy.int32)})
            result = cur.execute('SELECT * FROM pylite11').fetchdf()
            assert result['i'][0] == 0, "Invalid result"
            monetdbe.sql('DROP TABLE pylite11', client=conn)
            monetdbe.sql('ROLLBACK', client=conn)
            del conn

    def test_null_string_insertion_bug(self):
        con = monetdbe.connect()
        monetdbe.sql("CREATE TABLE pylite12 (s varchar(2))", client=con)
        monetdbe.insert('pylite12', {'s': ['a', None]}, client=con)
        result = monetdbe.sql("SELECT * FROM pylite12", client=con)
        expected = numpy.ma.masked_array(['a', 'a'], mask=[0, 1])
        numpy.testing.assert_array_equal(result['s'], expected)
