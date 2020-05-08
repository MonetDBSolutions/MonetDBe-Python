import pytest
import monetdbe


@pytest.mark.skipif(True, reason="monetdblite compatibl but: not supported yet")
class TestShutdown:
    def test_commited_on_restart(self, monetdbe_cursor_autocommit):
        (cursor, connection, dbfarm) = monetdbe_cursor_autocommit
        cursor.transaction()
        cursor.execute('CREATE TABLE integers (i INTEGER)')
        cursor.executemany('INSERT INTO integers VALUES (%s)', [[x] for x in range(3)])
        cursor.execute('SELECT * FROM integers')
        result = cursor.fetchall()
        assert result == [[0], [1], [2]], "Incorrect result returned"
        cursor.commit()
        connection.close()

        connection = monetdbe.make_connection(dbfarm)
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM integers')
        assert result == [[0], [1], [2]], "Incorrect result returned"

    def test_transaction_aborted_on_shutdown(self, monetdbe_cursor_autocommit):
        (cursor, connection, dbfarm) = monetdbe_cursor_autocommit
        cursor.transaction()
        cursor.execute('CREATE TABLE integers (i INTEGER)')
        cursor.executemany('INSERT INTO integers VALUES (%s)', [[x] for x in range(3)])
        cursor.execute('SELECT * FROM integers')
        result = cursor.fetchall()
        assert result == [[0], [1], [2]], "Incorrect result returned"
        connection.close()

        connection = monetdbe.make_connection(dbfarm)
        cursor = connection.cursor()
        with pytest.raises(monetdbe.DatabaseError):
            cursor.execute('SELECT * FROM integers')

    def test_many_shutdowns(self, monetdbe_cursor_autocommit):
        (cursor, connection, dbfarm) = monetdbe_cursor_autocommit
        for i in range(10):
            cursor.transaction()
            cursor.execute('CREATE TABLE integers (i INTEGER)')
            cursor.executemany('INSERT INTO integers VALUES (%s)', [[x] for x in range(10)])
            cursor.execute('SELECT MIN(i * 3 + 5) FROM integers')
            result = cursor.fetchall()
            assert result == [[5]], "Incorrect result returned"
            connection.close()

            connection = monetdbe.make_connection(dbfarm)
            connection.set_autocommit(True)
            cursor = connection.cursor()

    def test_fetchone_without_executing_raises(self, monetdbe_empty_cursor):
        with pytest.raises(monetdbe.ProgrammingError):
            monetdbe_empty_cursor.fetchone()

    def test_fetchall_without_executing_raises(self, monetdbe_empty_cursor):
        with pytest.raises(monetdbe.ProgrammingError):
            monetdbe_empty_cursor.fetchall()

    def test_fetchnumpy_without_executing_raises(self, monetdbe_empty_cursor):
        with pytest.raises(monetdbe.ProgrammingError):
            monetdbe_empty_cursor.fetchnumpy()

    def test_fetchdf_without_executing_raises(self, monetdbe_empty_cursor):
        with pytest.raises(monetdbe.ProgrammingError):
            monetdbe_empty_cursor.fetchdf()

    def test_execute_with_closed_cursor_raises(self, monetdbe_empty_cursor):
        monetdbe_empty_cursor.close()
        with pytest.raises(monetdbe.ProgrammingError):
            monetdbe_empty_cursor.execute("SELECT * FROM _tables")

    def test_fetchmany(self, monetdbe_cursor):
        monetdbe_cursor.execute("SELECT * FROM integers")

        counter = 0
        while counter < 10:
            r = monetdbe_cursor.fetchmany(2)
            assert len(r) == 2
            counter += len(r)

        assert counter == 10

    def test_fetchmany_without_explicit_size(self, monetdbe_cursor):
        assert monetdbe_cursor.arraysize == 1, "Incorrect default value for cursor.arraysize"
        monetdbe_cursor.arraysize = 2
        monetdbe_cursor.execute("SELECT * FROM integers")

        counter = 0
        while counter < 10:
            r = monetdbe_cursor.fetchmany()
            assert len(r) == 2
            counter += len(r)

        assert counter == 10

    def test_scroll(self, monetdbe_cursor):
        monetdbe_cursor.execute("SELECT * FROM integers")
        monetdbe_cursor.scroll(5)

        x = monetdbe_cursor.fetchone()
        assert x[0] == 6

    def test_scroll_raises_for_incorrect_mode(self, monetdbe_cursor):
        monetdbe_cursor.execute("SELECT * FROM integers")
        with pytest.raises(monetdbe.ProgrammingError):
            monetdbe_cursor.scroll(5, mode='abc')

    def test_scroll_raises_for_out_of_bounds_offset(self, monetdbe_cursor):
        monetdbe_cursor.execute("SELECT * FROM integers")
        with pytest.raises(IndexError):
            monetdbe_cursor.scroll(20)

    @pytest.mark.xfail(reason="We do not implement correctly the iterator protocol for py27")
    def test_cursor_iteration_protocol(self, monetdbe_cursor):
        monetdbe_cursor.execute("SELECT * FROM integers WHERE i IS NOT NULL")

        counter = 0
        for i in monetdbe_cursor:
            assert i[0] == counter
            counter += 1

        assert counter == 10
    # TODO: rewrite this one
    # def test_use_old_cursor(self, monetdbe_cursor):
    #     self.connection.close()

    #     self.connection = monetdbe.connect(self.dbfarm)
    #     if not PY26:
    #         with self.assertRaises(monetdbe.ProgrammingError):
    #             monetdbe_cursor.execute('SELECT * FROM integers')
