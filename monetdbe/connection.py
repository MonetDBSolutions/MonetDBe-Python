from typing import Optional, Type
from monetdbe.cursor import Cursor
from monetdbe.row import Row
from monetdbe._cffi import MonetEmbedded


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

    def __del__(self):
        ...

    def execute(self, query: str):
        return Cursor(con=self).execute(query)

    def executemany(self, *args, **kwargs):
        raise NotImplemented

    def commit(self, *args, **kwargs):
        raise NotImplemented

    def close(self, *args, **kwargs):
        del self.inter
        self.inter = None

    def cursor(self, factory: Type[Cursor] = Cursor):
        cursor = factory(con=self)
        if not cursor:
            raise TypeError
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
