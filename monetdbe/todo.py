"""
All the things that are not implemented yet
"""

PARSE_DECLTYPES = False
PARSE_COLNAMES = False

converters = {}

OptimizedUnicode = False


class Row:
    ...


def register_adapter(*args, **kwargs):
    ...


def register_converter(*args, **kwargs):
    ...


class Cursor:
    lastrowid = 0

    @property
    def description(self):
        return []

    def __init__(self, *args, **kwargs):
        ...

    def execute(self, *args, **kwargs):
        return self

    def executemany(self, *args, **kwargs):
        return []

    def close(self, *args, **kwargs):
        ...

    def fetchall(self, *args, **kwargs):
        return []

    def fetchmany(self, *args, **kwargs):
        return []

    def fetchone(self, *args, **kwargs):
        return []

    def executescript(self, *args, **kwargs):
        return []


class Connection:
    def __init__(self, *args, **kwargs):
        ...

    def __enter__(self, *args, **kwargs):
        return self

    def __exit__(self, *args, **kwargs):
        ...

    def execute(self, *args, **kwargs):
        return Cursor()

    def executemany(self, *args, **kwargs):
        ...

    def commit(self, *args, **kwargs):
        ...

    def close(self, *args, **kwargs):
        ...

    def cursor(self, *args, **kwargs):
        return Cursor()

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


def connect(*args, **kwargs):
    return Connection()
