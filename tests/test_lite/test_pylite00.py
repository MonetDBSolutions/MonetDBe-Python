import monetdbe
import numpy
import os
import shutil
import pytest


@pytest.mark.skipif(True, reason="monetdblite compatibl but: not supported yet")
class TestmonetdbeBase(object):
    def test_uninitialized(self):
        # select before init
        with pytest.raises(monetdbe.DatabaseError):
            monetdbe.sql('select * from tables')

    def test_regular_selection(self, initialize_monetdbe):
        monetdbe.sql('CREATE TABLE pylite00 (i INTEGER)')
        monetdbe.sql('INSERT INTO pylite00 VALUES (1), (2), (3), (4), (5)')
        result = monetdbe.sql('SELECT * FROM pylite00')
        assert len(result['i']) == 5, "Incorrect result"

    def test_monetdbe_create(self, initialize_monetdbe):
        monetdbe.create('pylite01', {'i': numpy.arange(100000)})
        result = monetdbe.sql('select * from pylite01')
        assert len(result['i']) == 100000, "Incorrect result"

    def test_monetdbe_insert(self, initialize_monetdbe):
        monetdbe.create('pylite02', {'i': numpy.arange(100000)})
        monetdbe.insert('pylite02', numpy.arange(100000))
        result = monetdbe.sql('select * from pylite02')
        assert len(result['i']) == 200000, "Incorrect result"

    def test_monetdbe_create_multiple_columns(self, initialize_monetdbe):
        arrays = numpy.arange(100000).reshape((5, 20000))
        monetdbe.create('pylite03', {'i': arrays[0], 'j': arrays[1], 'k': arrays[2], 'l': arrays[3], 'm': arrays[4]})
        result = monetdbe.sql('select * from pylite03')
        assert len(result) == 5, "Incorrect amount of columns"
        assert len(result['i']) == 20000, "Incorrect amount of rows"

    def test_sql_types(self, initialize_monetdbe):
        monetdbe.sql('CREATE TABLE pylite04_decimal(d DECIMAL(18,3))')
        monetdbe.insert('pylite04_decimal', {'d': numpy.arange(100000)})
        result = monetdbe.sql('SELECT * FROM pylite04_decimal')
        assert result['d'][0] == 0, "Incorrect result"

        monetdbe.sql('CREATE TABLE pylite04_date(d DATE)')
        monetdbe.sql("INSERT INTO pylite04_date VALUES ('2000-01-01')")
        result = monetdbe.sql('SELECT d FROM pylite04_date')
        assert result['d'][0] == '2000-01-01', "Incorrect result"

    def test_connections(self, initialize_monetdbe):
        # create two clients
        conn = monetdbe.connectclient()
        conn2 = monetdbe.connectclient()
        # create a table within a transaction in one client
        monetdbe.sql('START TRANSACTION', client=conn)
        monetdbe.create('pylite05', {'i': numpy.arange(100000)}, client=conn)

        # check that table was successfully created
        result = monetdbe.sql('SELECT MIN(i) AS minimum FROM pylite05', client=conn)
        assert result['minimum'][0] == 0, "Incorrect result"
        # attempt to query the table from another client
        if not PY26:
            with pytest.raises(monetdbe.DatabaseError):
                monetdbe.sql('SELECT * FROM pylite05', client=conn2)

        # now commit the table
        monetdbe.sql('COMMIT', client=conn)
        # query the table again from the other client, this time it should be there
        result = monetdbe.sql('SELECT MIN(i) AS minimum FROM pylite05', client=conn2)
        assert result['minimum'][0] == 0, "Incorrect result"

    def test_erroneous_initialization(self):
        # init with weird argument
        with pytest.raises(Exception):
            monetdbe.init(33)

    def test_non_existent_table(self, initialize_monetdbe):
        # select from non-existent table
        with pytest.raises(monetdbe.DatabaseError):
            monetdbe.sql('select * from nonexistenttable')

    def test_invalid_connection_object(self, initialize_monetdbe):
        # invalid connection object
        with pytest.raises(monetdbe.DatabaseError):
            monetdbe.sql('select * from tables', client=33)

    def test_invalid_colnames(self, initialize_monetdbe):
        # invalid colnames
        with pytest.raises(monetdbe.DatabaseError):
            monetdbe.create('pylite06', {33: []})

    @pytest.mark.xfail(reason='Bug in upstream MonetDB')
    def test_empty_colnames(self, initialize_monetdbe):
        # empty colnames
        with pytest.raises(monetdbe.DatabaseError):
            monetdbe.create('pylite07', {'': []})

    def test_invalid_key_dict(self, initialize_monetdbe):
        # dictionary with invalid keys
        d = dict()
        d[33] = 44
        with pytest.raises(monetdbe.DatabaseError):
            monetdbe.create('pylite08', d)

    @pytest.mark.skip(reason="segfault")
    def test_missing_dict_key(self, initialize_monetdbe):
        # FIXME: segfault
        # missing dict key in insert
        monetdbe.create('pylite09', dict(a=[], b=[], c=[]))
        with pytest.raises(monetdbe.DatabaseError):
            monetdbe.insert('pylite09', dict(a=33, b=44))

    def test_bad_column_number(self, initialize_monetdbe):
        # too few columns in insert
        monetdbe.create('pylite10', dict(a=[], b=[], c=[]))
        with pytest.raises(monetdbe.DatabaseError):
            monetdbe.insert('pylite10', [[33], [44]])

    def test_many_sql_statements(self, initialize_monetdbe):
        for i in range(5):  # FIXME 1000
            conn = monetdbe.connectclient()
            monetdbe.sql('START TRANSACTION', client=conn)
            monetdbe.sql('CREATE TABLE pylite11 (i INTEGER)', client=conn)
            monetdbe.insert('pylite11', {'i': numpy.arange(10)}, client=conn)
            result = monetdbe.sql('SELECT * FROM pylite11', client=conn)
            assert result['i'][0] == 0, "Invalid result"
            monetdbe.sql('DROP TABLE pylite11', client=conn)
            monetdbe.sql('ROLLBACK', client=conn)
            del conn

    def test_null_string_insertion_bug(self, initialize_monetdbe):
        monetdbe.sql("CREATE TABLE pylite12 (s varchar(2))")
        monetdbe.insert('pylite12', {'s': ['a', None]})
        result = monetdbe.sql("SELECT * FROM pylite12")
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
