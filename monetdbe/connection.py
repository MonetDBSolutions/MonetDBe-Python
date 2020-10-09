"""
This module contains the monetdbe connection class.
"""
from pathlib import Path
from typing import Optional, Type, Iterable, Union, TYPE_CHECKING, Callable, Any, Iterator

from monetdbe import exceptions

if TYPE_CHECKING:
    from monetdbe.row import Row
    from monetdbe.cursor import Cursor


class Connection:
    def __init__(self,
                 database: Optional[Union[str, Path]] = None,
                 uri: bool = False,
                 timeout: int = 0,
                 detect_types: int = 0,
                 check_same_thread: bool = True,
                 autocommit: bool = False,
                 nr_threads: int = 0,
                 memorylimit: int = 0,
                 querytimeout: int = 0,
                 logging: Optional[Path] = None,
                 username: Optional[str] = None,
                 password: Optional[str] = None,
                 port: Optional[int] = None,
                 ):
        """
        Args:
            database: The path to you database. Leave empty or use the `:memory:` string to start an in-memory database.
            uri: if true, database is interpreted as a URI. This allows you to specify options.
            timeout: The session / connection timeout in seconds, 0 = no limit (default)
            detect_types:  defaults to 0 (i. e. off, no type detection), you can set it to any combination of
                           PARSE_DECLTYPES and PARSE_COLNAMES to turn type detection on.
            check_same_thread: By default, check_same_thread is True and only the creating thread may use the
                               connection. If set False, the returned connection may be shared across multiple threads.
                               When using multiple threads with the same connection writing operations should be
                               serialized by the user to avoid data corruption.
            autocommit: Enable autocommit mode
            nr_threads: to control the level of parallelism, 0 = all cores (default)
            memorylimit: to control the memory footprint allowed in :memory: mode in MB, 0 = no limit (default)
            querytimeout: The query timeout in seconds, 0 = no limit (default)
            logging: the file location for the tracer files (not used yet)
            username: used to connect to a remote server (not used yet)
            password: credentials to reach the remote server (not used yet)
            port: TCP/IP port to listen for connections (not used yet)

        """
        if uri or port or username or password or logging:
            raise NotImplemented  # todo

        if not check_same_thread:
            raise NotImplemented  # todo

        if detect_types != 0:
            raise NotImplemented  # todo

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

        from monetdbe._cffi import check_if_we_can_import_lowlevel

        check_if_we_can_import_lowlevel()

        from monetdbe._cffi.frontend import Frontend

        self.lowlevel: Optional[Frontend] = Frontend(
            dbdir=database,
            memorylimit=memorylimit,
            nr_threads=nr_threads,
            querytimeout=querytimeout,
            sessiontimeout=timeout
        )

        self.result = None
        self.row_factory: Optional[Type[Row]] = None
        self.text_factory: Optional[Callable[[str], Any]] = None
        self.total_changes = 0
        self.isolation_level = None
        self.consistent = True

        self.set_autocommit(autocommit)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def __call__(self):
        raise exceptions.ProgrammingError

    def _check(self):
        if not self.lowlevel:
            raise exceptions.ProgrammingError

    def execute(self, query: str, args: Optional[Iterable] = None) -> 'Cursor':
        """
        Execute a SQL query

        This is a nonstandard and SQLite compatible shortcut that creates a cursor object by calling the cursor()
        method, calls the cursor’s execute() method with the parameters given, and returns the cursor.

        Args:
            query: The SQL query to execute
            args:  The optional SQL query arguments

        Returns:
            A new cursor.
        """
        from monetdbe.cursor import Cursor  # we need to import here, otherwise circular import
        cur = Cursor(con=self).execute(query, args)
        self.consistent = True
        return cur

    def executemany(self, query: str, args_seq: Union[Iterator, Iterable[Iterable]]) -> 'Cursor':
        """
        Prepare a database query and then execute it against all parameter sequences or mappings found in the
        sequence seq_of_parameters.

        This is a nonstandard and SQLite compatible shortcut that creates a cursor object by calling the cursor()
        method, calls the cursor’s execute() method with the parameters given, and returns the cursor.

        Args:
            query: The SQL query to execute
            args:  The optional SQL query arguments

        Returns:
            A new cursor.
        """
        from monetdbe.cursor import Cursor
        cur = Cursor(con=self)
        for args in args_seq:
            cur.execute(query, args)
        return cur

    def commit(self, *args, **kwargs) -> 'Cursor':
        self._check()
        return self.execute("COMMIT")

    def close(self, *args, **kwargs) -> None:
        if self.lowlevel:
            self.lowlevel.close()
        self.lowlevel = None

    def cursor(self, factory: Optional[Type['Cursor']] = None) -> 'Cursor':
        """
        Create a new cursor.

        Args:
            factory: An optional factory. If supplied, this must be a callable returning an instance of Cursor or its
                     subclasses.

        Returns:
            a new cursor.
        """

        if not factory:
            from monetdbe.cursor import Cursor
            factory = Cursor

        cursor = factory(con=self)
        if not cursor:
            raise TypeError
        if not hasattr(self, 'lowlevel') or not self.lowlevel:
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
        """
        Rolls back the current transaction.
        """
        self._check()
        self.execute("ROLLBACK")
        self.consistent = False

    @property
    def in_transaction(self):
        return self.lowlevel.in_transaction()

    def set_autocommit(self, value: bool) -> None:
        """
        Set the connection to auto-commit mode.

        Args:
            value: a boolean value
        """
        self._check()
        return self.lowlevel.set_autocommit(value)  # type: ignore

    def read_csv(self, table, *args, **kwargs):
        from monetdbe.cursor import Cursor  # we need to import here, otherwise circular import
        cur = Cursor(con=self).read_csv(table, *args, **kwargs)

    def write_csv(self, table, *args, **kwargs):
        from monetdbe.cursor import Cursor  # we need to import here, otherwise circular import
        cur = Cursor(con=self).write_csv(table, *args, **kwargs)

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
