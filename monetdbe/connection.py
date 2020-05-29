from pathlib import Path
from typing import Optional, Type, Iterable, Union, TYPE_CHECKING, Callable, Any
from warnings import warn

from monetdbe import exceptions
from monetdbe._cffi import MonetEmbedded

if TYPE_CHECKING:
    from monetdbe.row import Row
    from monetdbe.cursor import Cursor


class Connection:
    def __init__(self,
                 database: Optional[Union[str, Path]] = None,
                 uri: bool = False,
                 timeout: float = 5.0,
                 detect_types: int = 0,
                 check_same_thread: bool = True):
        """
        args:
            uri: if true, database is interpreted as a URI. This allows you to specify options. For example, to open a
                 database in read-only mode you can use:
        """
        if uri:
            raise NotImplemented

        if not check_same_thread:
            raise NotImplemented

        if not database:
            database = None
        elif database == ':memory:':  # sqlite compatibility
            database = None
        elif type(database) == str:
            database = Path(database).resolve()
        elif hasattr(database, '__fspath__'):  # Deal with Path like objects
            database = Path(database.__fspath__()).resolve()  # type: ignore
        else:
            raise TypeError

        try:
            self.inter = MonetEmbedded(dbdir=database)
        except exceptions.DatabaseError as e:
            raise exceptions.OperationalError(e)

        self.result = None
        self.row_factory: Optional[Type[Row]] = None
        self.text_factory: Optional[Callable[[str], Any]] = None
        self.total_changes = 0
        self.isolation_level = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def __call__(self):
        raise exceptions.ProgrammingError

    def _check(self):
        if not self.inter:
            raise exceptions.ProgrammingError

    def execute(self, query: str, args: Optional[Iterable] = None):
        from monetdbe.cursor import Cursor
        return Cursor(con=self).execute(query, args)

    def executemany(self, query: str, args_seq: Iterable):
        from monetdbe.cursor import Cursor
        cur = Cursor(con=self)
        for args in args_seq:
            cur.execute(query, args)
        return cur

    def commit(self, *args, **kwargs):
        # todo: not implemented yet on monetdb side
        self._check()
        # raise NotImplemented

    def close(self, *args, **kwargs):
        del self.inter
        self.inter = None

    def cursor(self, factory: Optional[Type['Cursor']] = None):

        if not factory:
            from monetdbe.cursor import Cursor
            factory = Cursor

        cursor = factory(con=self)
        if not cursor:
            raise TypeError
        if not self.inter:
            raise exceptions.ProgrammingError
        return cursor

    def executescript(self, sql_script: str):
        self._check()
        for query in sql_script.split(';'):
            query = query.strip()
            if query:
                self.execute(query)

    def set_authorizer(self, *args, **kwargs):
        self._check()
        raise NotImplemented

    def backup(self, *args, **kwargs):
        self._check()
        raise NotImplemented

    def iterdump(self, *args, **kwargs):
        self._check()
        raise NotImplemented

    def create_collation(self, *args, **kwargs):
        self._check()
        raise NotImplemented

    def create_aggregate(self, *args, **kwargs):
        self._check()
        raise NotImplemented

    def set_progress_handler(self, *args, **kwargs):
        self._check()
        raise NotImplemented

    def set_trace_callback(self, *args, **kwargs):
        self._check()
        raise NotImplemented

    def create_function(self, *args, **kwargs):
        self._check()
        raise NotImplemented

    def rollback(self, *args, **kwargs):
        self._check()
        raise NotImplemented

    @property
    def in_transaction(self):
        raise NotImplemented

    def set_autocommit(self):
        warn("set_autocommit() will be deprecated in future releases")
        self._check()
        raise NotImplemented

    # these are required by the python DBAPI
    Warning = exceptions.Warning
    Error = exceptions.Error
    InterfaceError = exceptions.InterfaceError
    DatabaseError = exceptions.DatabaseError
    DataError = exceptions.DataError
    OperationalError = exceptions.OperationalError
    IntegrityError = exceptions.IntegrityError
    InternalError = exceptions.InternalError
    ProgrammingError = exceptions.ProgrammingError
    NotSupportedError = exceptions.NotSupportedError
