from typing import Optional, Type
from monetdbe.cursor import Cursor
from monetdbe._cffi import MonetEmbedded


class Connection:
    def __init__(self, database: Optional[str] = None):
        if database == ':memory:':
            database = None
        self.inter = MonetEmbedded(dbdir=database)
        self.result = None

    def __enter__(self, *args, **kwargs):
        return self

    def __exit__(self, *args, **kwargs):
        ...

    def __del__(self):
        # self.inter.cleanup_result(self.result)
        ...

    def execute(self, query: str):
        return Cursor(con=self).execute(query)

    def executemany(self, *args, **kwargs):
        ...

    def commit(self, *args, **kwargs):
        ...

    def close(self, *args, **kwargs):
        ...

    def cursor(self, factory: Type[Cursor] = Cursor):
        cursor = factory(con=self)
        if not cursor:
            raise TypeError
        return cursor

    def executescript(self, *args, **kwargs):
        ...

    def set_authorizer(self, *args, **kwargs):
        ...

    def backup(self, *args, **kwargs):
        ...

    def iterdump(self, *args, **kwargs):
        ...

    def create_collation(self, *args, **kwargs):
        ...

    def create_aggregate(self, *args, **kwargs):
        ...

    def set_progress_handler(self, *args, **kwargs):
        ...

    def set_trace_callback(self, *args, **kwargs):
        ...

    def create_function(self, *args, **kwargs):
        ...

    def rollback(self, *args, **kwargs):
        ...

    @property
    def isolation_level(self):
        ...
