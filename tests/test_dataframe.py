from datetime import datetime
from typing import List, Any
from unittest import TestCase
from math import isnan

import numpy as np
import numpy.ma as ma
from pandas import DataFrame
from monetdbe import connect, Timestamp


def connect_and_execute(values: List[Any], type: str) -> DataFrame:
    with connect(autocommit=True) as con:
        cur = con.execute(f"create table example(d {type})")
        cur.executemany("insert into example(d) values (?)", ((v,) for v in values))
        cur.execute("select * from example")
        return cur.fetchdf()


def connect_and_append(values: List[Any], type: str, to_numpy=True) -> DataFrame:
    with connect(autocommit=True) as con:
        cur = con.execute(f"create table example(d {type})")
        input = np.array(values) if to_numpy else values
        con.append(table='example', data={'d': input})
        cur.execute("select * from example")
        return cur.fetchdf()


class TestDataFrame(TestCase):
    def test_timestamp(self):
        now = datetime.now().replace(microsecond=0)  # monetdb doesn't support microseconds
        values = [
            now,
            Timestamp(2004, 2, 14, 7, 15, 0, 510000),
        ]
        df = connect_and_execute(values, 'timestamp')
        self.assertEqual(values, list(df['d']))

    def test_int(self):
        values = [5, 10, -100]
        df = connect_and_execute(values, 'int')
        self.assertEqual(values, list(df['d']))

    def test_int_append(self):
        values = [5, 10, -100]
        df = connect_and_append(values, 'int')
        self.assertEqual(values, list(df['d']))

    def test_float(self):
        values = [5.0, 10.0, -100.0, float('nan')]
        df = connect_and_execute(values, 'float')
        self.assertEqual(values[:-1], list(df['d'])[:-1])
        self.assertTrue(isnan(df['d'].iloc[-1]))

    def test_float_append(self):
        values = [5.0, 10.0, -100.0, float('nan')]
        df = connect_and_append(values, 'float')
        self.assertEqual(values[:-1], list(df['d'])[:-1])
        self.assertTrue(isnan(df['d'].iloc[-1]))

    def test_char(self):
        values = ['a', 'i', 'é']
        df = connect_and_execute(values, 'char')
        self.assertEqual(values, list(df['d']))

    def test_string(self):
        values = ['asssssssssssssssss', 'iwwwwwwwwwwwwwww', 'éooooooooooooooooooooo']
        df = connect_and_execute(values, 'string')
        self.assertEqual(values, list(df['d']))

    def test_string_append(self):
        values = ['asssssssssssssssss', 'iwwwwwwwwwwwwwww', 'éooooooooooooooooooooo']
        df = connect_and_append(values, 'string')
        self.assertEqual(values, list(df['d']))

    def test_string_nil_append(self):
        values = np.array(['asssssssssssssssss', 'iwwwwwwwwwwwwwww', None], dtype=np.str_)

        masked = ma.masked_array(values, mask=[0, 0, 1])
        df = connect_and_append(masked, 'string', False)
        self.assertEqual(masked.tolist(), list(df['d'].replace({np.nan: None})))

    def test_varchar(self):
        values = ['a', 'aa', 'éooooooooooooooooooooo']
        df = connect_and_execute(values, 'string')
        self.assertEqual(values, list(df['d']))

    def test_uuid(self):
        values = ['6c49869d-45dc-4b00-ae55-5bd363c0c72c', '2ad49a96-ba10-11ea-b3de-0242ac130004']
        df = connect_and_execute(values, 'uuid')
        self.assertEqual(values, list(df['d']))

    def test_datetime(self):
        values = np.array(['2001-01-01T12:00', '2002-02-03T13:56:03.172'], dtype='datetime64')
        values = list(values)
        df = connect_and_append(values, 'timestamp')
        self.assertEqual(values, list(df['d']))

    def test_datetime_nil(self):
        values = np.array(['nat', '2002-02-03T13:56:03.172'], dtype='datetime64')
        df = connect_and_append(values, 'timestamp')

        """
        NOTE: Unfortunately panda's only allows ns as unit of precision.
        Hence we need to cast back to numpy to restore to ms precision.
        """
        result = df['d'].values.astype('datetime64[ms]')
        self.assertEqual(values.tolist(), result.tolist())

    def test_date_nil(self):
        values = np.array(['nat', '2002-02-03'], dtype='datetime64[D]')
        df = connect_and_append(values, 'date')

        result = df['d'].values.astype('datetime64[D]')
        self.assertEqual(values.tolist(), result.tolist())
