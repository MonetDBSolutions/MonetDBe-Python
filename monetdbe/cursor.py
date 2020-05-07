from typing import TYPE_CHECKING, Tuple

from monetdbe._cffi import extract, make_string

if TYPE_CHECKING:
    from monetdbe.connection import Connection


class Cursor:
    lastrowid = 0

    def __init__(self, con: 'Connection'):
        if not con:
            raise TypeError
        self.con = con
        self.result = None
        self.affected_rows = None
        self.prepare_id = None
        self._all = None
        self.description: Tuple[str] = tuple()

    def execute(self, operation: str, parameters=None):
        self.description = None  # which will be set later in fetchall
        self.result, self.affected_rows, self.prepare_id = self.con.inter.query(operation, make_result=True)
        return self

    def executemany(self, *args, **kwargs):
        raise NotImplemented

    def close(self, *args, **kwargs):
        raise NotImplemented

    def fetchall(self):
        columns = list(map(lambda x: self.con.inter.result_fetch(self.result, x), range(self.result.ncols)))
        for r in range(self.result.nrows):
            if not self.description:
                # todo: make_string(rcol.name)
                self.description = tuple(rcol.name for rcol in columns)
            row = (extract(rcol, r) for rcol in columns)
            if self.con.row_factory:
                yield self.con.row_factory(cur=self, row=row)
            else:
                yield row

    def fetchmany(self, *args, **kwargs):
        raise NotImplemented

    def fetchone(self, *args, **kwargs):
        if not self._all:
            self._all = self.fetchall()
        return next(self._all)

    def executescript(self, *args, **kwargs):
        raise NotImplemented
