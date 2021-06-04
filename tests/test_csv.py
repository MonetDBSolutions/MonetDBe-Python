from monetdbe import connect
from unittest import TestCase
from pathlib import Path
from tempfile import TemporaryDirectory


class TestCsv(TestCase):
    def test_read_csv(self):
        table = 'test'
        con = connect()

        con.read_csv(
            table=table,
            filepath_or_buffer=Path(__file__).parent / "example.csv",
            names=['i', 's', 'i2', 'f'],
            dtype={"i1": int, 's': str, 'i2': int, 'f': float},
        )
        x = con.execute(f'select * from {table}').fetchall()

    def test_write_csv(self):
        con = connect()
        t = TemporaryDirectory()

        con.write_csv(table='tables', path_or_buf=Path(t.name) / 'output.csv')

    def test_copy_into_windows(self):
        con = connect()
        s = """COPY OFFSET 2 INTO t FROM 'C:\\does\\not\\exist.csv' delimiters ',','"""
        con.execute(s)

    def test_copy_into_windows_double_escape(self):
        con = connect()
        s = """COPY OFFSET 2 INTO t FROM 'C:\\\\does\\not\\\\exist.csv' delimiters ',','"""
        con.execute(s)