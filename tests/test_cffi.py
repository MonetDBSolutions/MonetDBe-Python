import unittest

from monetdbe._lowlevel import lib

from monetdbe import connect

class TestCffi(unittest.TestCase):
    def test_cffi(self):
        self.assertEqual(lib.monetdbe_float, 6)

    def test_append_supported_types(self):
        con = connect()
        con.execute("CREATE TABLE test (t tinyint, s smallint, i int, b bigint, r real, f float)")
        con.execute(
            """
            INSERT INTO test VALUES (2^8,  2^16,  2^32,  2^64,  0.12345,  0.123456789),
                                    (NULL, NULL,  NULL,  NULL,  NULL,     NULL),
                                    (0,    0,     0,     0,     0.0,      0.0),
                                    (-2^8, -2^16, -2^32, -2^64, -0.12345, -0.123456789)
            """
        )
        data = con.execute("select * from test").fetchnumpy()
        con.lowlevel.append(schema='sys', table='test', data=data)
        con.cursor().insert(table='test', values=data)

    def test_append_unsupported_types(self):
        con = connect()
        con.execute("CREATE TABLE test (s string, b blob, d date, t time, ts timestamp)")
        con.execute(
            """
            INSERT INTO test VALUES ('hi',    '01020308', '2020-01-02', '10:20:30', '2020-01-02 10:20:30' ),
                                    ('World', NULL,       NULL,         NULL,       NULL )
            """
        )

        data = con.execute("select * from test").fetchnumpy()
        with self.assertRaises(con.ProgrammingError):
            con.lowlevel.append(schema='sys', table='test', data=data)
        con.cursor().insert(table='test', values=data)

    def test_append_blend(self):
        con = connect()
        con.execute("CREATE TABLE test (i int, f float, s string, ts timestamp)")
        con.execute(
            """
            INSERT INTO test VALUES (1, 1.2, 'bla', '2020-01-02 10:20:30'),
                                    (NULL, NULL, NULL, NULL)
            """
        )

        data = con.execute("select * from test").fetchnumpy()
        with self.assertRaises(con.ProgrammingError):
            con.lowlevel.append(schema='sys', table='test', data=data)
        con.cursor().insert(table='test', values=data)
