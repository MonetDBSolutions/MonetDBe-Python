import unittest
import numpy as np
from monetdbe._lowlevel import lib
from monetdbe import connect
from monetdbe.exceptions import ProgrammingError


class TestCffi(unittest.TestCase):
    def test_cffi(self):
        # if this tests fails you probably compiled monetdb with 128 bit support
        self.assertEqual(lib.monetdbe_type_unknown, 13)

    def test_append_too_many_columns(self):
        con = connect()
        con.execute("CREATE TABLE test (i int)")
        data = {'i': np.array([1, 2, 3]), 'j': np.array([1, 2, 3])}
        with self.assertRaises(ProgrammingError):
            con.lowlevel.append(table='test', data=data)

    def test_append_too_little_columns(self):
        con = connect()
        con.execute("CREATE TABLE test (i int, j int)")
        data = {'i': np.array([1, 2, 3])}
        with self.assertRaises(ProgrammingError):
            con.lowlevel.append(table='test', data=data)

    def test_append_wrong_type(self):
        con = connect()
        con.execute("CREATE TABLE test (i int)")
        data = {'i': np.array([0.1, 0.2, 0.3], dtype=np.float32)}
        with self.assertRaises(ProgrammingError):
            con.lowlevel.append(table='test', data=data)

    def test_append_wrong_size(self):
        con = connect()
        con.execute("CREATE TABLE test (i int)")  # SQL int is 32 bit
        data = {'i': np.array([1, 2, 3], dtype=np.int64)}
        with self.assertRaises(ProgrammingError):
            con.lowlevel.append(table='test', data=data)

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

    def test_get_columns(self):
        con = connect()
        con.execute("CREATE TABLE test (i int)")
        con.execute("INSERT INTO test VALUES (1)")
        result = list(con.lowlevel.get_columns(table='test'))
        self.assertEqual(result, [('i', 3)])
