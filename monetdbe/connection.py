from typing import Optional, Type, Iterable
from monetdbe.cursor import Cursor
from monetdbe.row import Row
from monetdbe._cffi import MonetEmbedded
from monetdbe.exceptions import ProgrammingError


class Connection:
    def __init__(self, database: Optional[str] = None):
        if database == ':memory:':
            database = None
        self.inter = MonetEmbedded(dbdir=database)
        self.result = None
        self.row_factory: Optional[Type[Row]] = None

    def __enter__(self, *args, **kwargs):
        return self

    def __exit__(self, *args, **kwargs):
        raise NotImplemented

    def __call__(self):
        raise ProgrammingError

    def execute(self, query: str):
        return Cursor(con=self).execute(query)

    def executemany(self, query: str, args_seq: Iterable):
        cur = Cursor(con=self)
        for args in args_seq:
            cur.execute(query, args)
        return cur

    def commit(self, *args, **kwargs):
        # todo: not implemented yet on monetdb side
        if not self.inter:
            raise ProgrammingError

    def close(self, *args, **kwargs):
        del self.inter
        self.inter = None

    def cursor(self, factory: Type[Cursor] = Cursor):
        cursor = factory(con=self)
        if not cursor:
            raise TypeError
        if not self.inter:
            raise ProgrammingError
        return cursor

    def executescript(self, *args, **kwargs):
        raise NotImplemented

    def set_authorizer(self, *args, **kwargs):
        raise NotImplemented

    def backup(self, *args, **kwargs):
        raise NotImplemented

    def iterdump(self, *args, **kwargs):
        raise NotImplemented

    def create_collation(self, *args, **kwargs):
        raise NotImplemented

    def create_aggregate(self, *args, **kwargs):
        raise NotImplemented

    def set_progress_handler(self, *args, **kwargs):
        raise NotImplemented

    def set_trace_callback(self, *args, **kwargs):
        raise NotImplemented

    def create_function(self, *args, **kwargs):
        raise NotImplemented

    def rollback(self, *args, **kwargs):
        raise NotImplemented

    @property
    def isolation_level(self):
        raise NotImplemented
