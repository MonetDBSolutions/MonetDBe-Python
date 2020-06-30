from datetime import datetime
from typing import List, Any
from unittest import TestCase
from math import isnan
from pandas import DataFrame

from monetdbe import connect, Timestamp


def _connect(values: List[Any], type: str) -> DataFrame:
    con = connect(autocommit=True)
    cur = con.execute(f"create table example(d {type})")
    cur.executemany("insert into example(d) values (?)", ((v,) for v in values))
    cur.execute("select * from example")
    return cur.fetchdf()


class TestDataFrame(TestCase):
    def test_timestamp(self):
        now = datetime.now().replace(microsecond=0)  # monetdb doesn't support microseconds
        values = [
            now,
            Timestamp(2004, 2, 14, 7, 15, 0, 510000),
        ]
        df = _connect(values, 'timestamp')
        self.assertEqual(values, list(df['d']))

    def test_int(self):
        values = [5, 10, -100]
        df = _connect(values, 'int')
        self.assertEqual(values, list(df['d']))

    def test_float(self):
        values = [5.0, 10.0, -100.0, float('nan')]
        df = _connect(values, 'float')
        self.assertEqual(values[:-1], list(df['d'])[:-1])
        self.assertTrue(isnan(df['d'].iloc[-1]))

    def test_char(self):
        values = ['a', 'i', 'é']
        df = _connect(values, 'char')
        self.assertEqual(values, list(df['d']))

    def test_string(self):
        values = ['asssssssssssssssss', 'iwwwwwwwwwwwwwww', 'éooooooooooooooooooooo']
        df = _connect(values, 'string')
        self.assertEqual(values, list(df['d']))

    def test_varchar(self):
        values = ['a', 'aa', 'éooooooooooooooooooooo']
        df = _connect(values, 'string')
        self.assertEqual(values, list(df['d']))

    def test_uuid(self):
        values = ['6c49869d-45dc-4b00-ae55-5bd363c0c72c', '2ad49a96-ba10-11ea-b3de-0242ac130004']
        df = _connect(values, 'uuid')
        self.assertEqual(values, list(df['d']))
