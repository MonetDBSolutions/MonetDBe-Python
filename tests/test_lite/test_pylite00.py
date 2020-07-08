import os
import shutil
from unittest import TestCase, skip

import numpy
import pytest

import monetdbe


@skip("work in progress, issue #43")
class TestmonetdbeBase(TestCase):
    def setUp(self) -> None:
        self.con = monetdbe.connect()

    def test_regular_selection(self):
        con = monetdbe.connect()
        monetdbe.sql('CREATE TABLE pylite00 (i INTEGER)', client=con)
        con.execute('INSERT INTO pylite00 VALUES (1), (2), (3), (4), (5)')
        result = con.execute('SELECT * FROM pylite00').fetchall()
        assert len(result['i']) == 5, "Incorrect result"

    def test_monetdbe_create(self):
        cur = monetdbe.create('pylite01', {'i': numpy.arange(100000)})
        result = monetdbe.sql('select * from pylite01', client=cur.connection)
        assert len(result['i']) == 100000, "Incorrect result"

    def test_monetdbe_insert(self):
        cur = monetdbe.create('pylite02', {'i': numpy.arange(100000)})
        cur.insert('pylite02', numpy.arange(100000))
        result = monetdbe.sql('select * from pylite02', client=cur.connection)
        assert len(result['i']) == 200000, "Incorrect result"

    def test_monetdbe_create_multiple_columns(self):
        arrays = numpy.arange(100000).reshape((5, 20000))
        cur = monetdbe.create('pylite03',
                              {'i': arrays[0], 'j': arrays[1], 'k': arrays[2], 'l': arrays[3], 'm': arrays[4]})
        result = monetdbe.sql('select * from pylite03', client=cur.connection)
        assert len(result) == 5, "Incorrect amount of columns"
        assert len(result['i']) == 20000, "Incorrect amount of rows"

    def test_sql_types(self):
        con = monetdbe.connect()
        con.execute('CREATE TABLE pylite04_decimal(d DECIMAL(18,3))')
        monetdbe.insert('pylite04_decimal', {'d': numpy.arange(100000)}, client=con)
        result = monetdbe.sql('SELECT * FROM pylite04_decimal')
        assert result['d'][0] == 0, "Incorrect result"

        monetdbe.sql('CREATE TABLE pylite04_date(d DATE)')
        monetdbe.sql("INSERT INTO pylite04_date VALUES ('2000-01-01')")
        result = monetdbe.sql('SELECT d FROM pylite04_date')
        assert result['d'][0] == '2000-01-01', "Incorrect result"

    def test_connections(self):
        # create two clients
        conn = monetdbe.connect(autocommit=True)
        conn2 = monetdbe.connect()
        # create a table within a transaction in one client
        monetdbe.sql('START TRANSACTION', client=conn)
        monetdbe.create('pylite05', {'i': numpy.arange(100000)}, client=conn)

        # check that table was successfully created
        result = monetdbe.sql('SELECT MIN(i) AS minimum FROM pylite05', client=conn)
        assert result['minimum'][0] == 0, "Incorrect result"
        # attempt to query the table from another client
        with pytest.raises(monetdbe.DatabaseError):
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

    @pytest.mark.xfail(reason='Bug in upstream MonetDB')
    def test_empty_colnames(self):
        # empty colnames
        with pytest.raises(monetdbe.DatabaseError):
            monetdbe.create('pylite07', {'': []})

    def test_invalid_key_dict(self):
        # dictionary with invalid keys
        d = dict()
        d[33] = 44
        with pytest.raises(monetdbe.DatabaseError):
            monetdbe.create('pylite08', d)

    @pytest.mark.skip(reason="segfault")
    def test_missing_dict_key(self, ):
        # FIXME: segfault
        # missing dict key in insert
        monetdbe.create('pylite09', dict(a=[], b=[], c=[]))
        with pytest.raises(monetdbe.DatabaseError):
            monetdbe.insert('pylite09', dict(a=33, b=44))

    def test_bad_column_number(self):
        # too few columns in insert
        monetdbe.create('pylite10', dict(a=[], b=[], c=[]))
        with pytest.raises(monetdbe.DatabaseError):
            monetdbe.insert('pylite10', [[33], [44]])

    def test_many_sql_statements(self):
        for i in range(5):  # FIXME 1000
            conn = monetdbe.connect()
            monetdbe.sql('START TRANSACTION', client=conn)
            monetdbe.sql('CREATE TABLE pylite11 (i INTEGER)', client=conn)
            monetdbe.insert('pylite11', {'i': numpy.arange(10)}, client=conn)
            result = monetdbe.sql('SELECT * FROM pylite11', client=conn)
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

    # This test must be executed after all others because it
    # initializes monetdbe independently out of the fixture
    # initialize_monetdbe
    @pytest.mark.xfail(reason="We should not be testing as root!")
    def test_unwriteable_dir(self):
        # init in unwritable directory
        os.mkdir('/tmp/unwriteabledir')
        os.chmod('/tmp/unwriteabledir', 0o555)
        with pytest.raises(monetdbe.DatabaseError):
            monetdbe.init('/tmp/unwriteabledir')

        monetdbe.shutdown()
        os.chmod('/tmp/unwriteabledir', 0o755)
        shutil.rmtree('/tmp/unwriteabledir')
