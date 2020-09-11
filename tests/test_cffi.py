import unittest

from monetdbe._lowlevel import lib

from monetdbe import connect


class TestCffi(unittest.TestCase):
    def test_cffi(self):
        self.assertEqual(lib.monetdbe_float, 6)

    def test_append(self):
        con = connect()
        con.execute("CREATE TABLE test (x integer, y string, ts timestamp, dt date, t time, b blob)")
        con.execute(
            """
            INSERT INTO test VALUES (42, 'Hello', '2020-01-02 10:20:30', '2020-01-02', '10:20:30', '01020308'), 
                        (NULL, 'World', NULL, NULL, NULL, NULL),
                        (NULL, 'Foo', NULL, NULL, NULL, NULL),
                        (43, 'Bar', '2021-02-03 11:21:31', '2021-02-03', '11:21:31', '01020306')
            """
        )

        data = con.execute("select * from test").fetchnumpy()
        con.lowlevel.append_numpy(schema='sys', table='test', data=data)
