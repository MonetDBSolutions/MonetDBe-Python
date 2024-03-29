from monetdbe import connect
from unittest import TestCase
from pathlib import Path
from tempfile import TemporaryDirectory


class TestCsv(TestCase):
    def test_read_csv(self):
        table = 'test'
        with connect(autocommit=True) as con:
            con.read_csv(
                table=table,
                filepath_or_buffer=Path(__file__).parent / "example.csv",
                names=['i1', 's', 'i2', 'f'],
                dtype={'i1': int, 's': str, 'i2': int, 'f': float},
            )
            x = con.execute(f'select * from {table}').fetchall()

    def test_write_csv(self):
        with connect(autocommit=True) as con:
            t = TemporaryDirectory()

            con.write_csv(table='tables', path_or_buf=Path(t.name) / 'output.csv')
