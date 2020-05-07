import typing

from monetdbe._cffi import extract

if typing.TYPE_CHECKING:
    from monetdbe.connection import Connection


class Cursor:
    lastrowid = 0

    @property
    def description(self):
        return []

    def __init__(self, con: 'Connection'):
        if not con:
            raise TypeError
        self.con = con
        self.result = None
        self.affected_rows = None
        self.prepare_id = None
        self.all = None

    def execute(self, operation: str, parameters=None):
        self.result, self.affected_rows, self.prepare_id = self.con.inter.query(operation, make_result=True)
        return self

    def executemany(self, *args, **kwargs):
        raise NotImplemented

    def close(self, *args, **kwargs):
        ...

    def fetchall(self):
        columns = list(map(lambda x: self.con.inter.result_fetch(self.result, x), range(self.result.ncols)))
        for r in range(self.result.nrows):
            yield [extract(rcol, r) for rcol in columns]

    def fetchmany(self, *args, **kwargs):
        raise NotImplemented

    def fetchone(self, *args, **kwargs):
        if not self.all:
            self.all = self.fetchall()
        return next(self.all)

    def executescript(self, *args, **kwargs):
        raise NotImplemented
