import typing

from monetdbe._cffi import extract

if typing.TYPE_CHECKING:
    from monetdbe.connection import Connection


class Cursor:
    lastrowid = 0

    @property
    def description(self):
        return []

    def __init__(self, connection: 'Connection'):
        self.connection = connection
        self.result = None
        self.affected_rows = None
        self.prepare_id = None

    def execute(self, operation: str, parameters=None):
        self.result, self.affected_rows, self.prepare_id = self.connection.execute(operation)

    def executemany(self, *args, **kwargs):
        return []

    def close(self, *args, **kwargs):
        ...

    def fetchall(self):
        columns = list(map(lambda x: self.connection.inter.result_fetch(self.result, x), range(self.result.ncols)))
        for r in range(self.result.nrows):
            yield [extract(rcol, r) for rcol in columns]

    def fetchmany(self, *args, **kwargs):
        return []

    def fetchone(self, *args, **kwargs):
        return []

    def executescript(self, *args, **kwargs):
        return []
