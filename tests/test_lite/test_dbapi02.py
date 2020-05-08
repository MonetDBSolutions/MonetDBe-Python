import monetdbe.monetize
import numpy

identifier_escape = monetdbe.monetize.monet_identifier_escape


class TestMultipleResultSets:
    def test_string_insertion(self, monetdbe_cursor):
        monetdbe_cursor.execute('CREATE TABLE strings(s STRING)')
        monetdbe_cursor.executemany('INSERT INTO strings VALUES (%s)', ["'hello\" world\"'"])
        monetdbe_cursor.execute('SELECT * FROM strings')
        result = monetdbe_cursor.fetchall()
        assert result == [["'hello\" world\"'"]], "Incorrect result returned"

    def test_table_name(self, monetdbe_cursor):
        sname = "table"
        tname = 'integer'
        monetdbe_cursor.execute('CREATE SCHEMA %s' % identifier_escape(sname))
        monetdbe_cursor.create(tname, {'i': numpy.arange(3)}, schema=sname)
        monetdbe_cursor.execute('SELECT * FROM %s.%s' % (identifier_escape(sname), identifier_escape(tname)))
        result = monetdbe_cursor.fetchall()
        assert result == [[0], [1], [2]], "Incorrect result returned"
