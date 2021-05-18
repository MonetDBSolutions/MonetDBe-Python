"""
This module contains the monetdbe connection class.
"""
from collections import namedtuple
from pathlib import Path
from typing import Optional, Type, Iterable, Union, TYPE_CHECKING, Callable, Any, Iterator, Tuple, Mapping
from itertools import repeat
import numpy as np

from monetdbe import exceptions
from monetdbe.formatting import parameters_type

if TYPE_CHECKING:
    from monetdbe.row import Row
    from monetdbe.cursors import Cursor  # type: ignore[attr-defined]

Description = namedtuple('Description', (
    'name',
    'type_code',
    'display_size',
    'internal_size',
    'precision',
    'scale',
    'null_ok'
))


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
        # import these here so we can import this file without having access to _cffi (yet)
        from monetdbe._cffi import check_if_we_can_import_lowlevel
        from monetdbe._cffi.internal import Internal
        from monetdbe._cffi.types_ import monetdbe_result

        check_if_we_can_import_lowlevel()

        if uri or port or username or password or logging:
            raise NotImplemented

        if not check_same_thread:
            raise NotImplemented

        if detect_types != 0:
            raise NotImplemented

        if not database:
            database = None
        elif database == ':memory:':  # sqlite compatibility
            database = None
        elif isinstance(database, str):
            database = Path(database).resolve()
        elif hasattr(database, '__fspath__'):  # Deal with Path like objects
            database = Path(database.__fspath__()).resolve()  # type: ignore
        else:
            raise TypeError

        self.result: Optional[monetdbe_result] = None
        self.row_factory: Optional[Type['Row']] = None
        self.text_factory: Optional[Callable[[str], Any]] = None
        self.total_changes = 0
        self.isolation_level = None
        self.consistent = True

        self._internal: Optional[Internal] = Internal(
            connection=self,
            dbdir=database,
            memorylimit=memorylimit,
            nr_threads=nr_threads,
            querytimeout=querytimeout,
            sessiontimeout=timeout
        )

        self.set_autocommit(autocommit)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def __call__(self):
        raise exceptions.ProgrammingError

    def __del__(self):
        self.close()

    def _check(self):
        if not hasattr(self, '_internal') or not self._internal:
            raise exceptions.ProgrammingError("The connection has been closed")

    def get_description(self):
        # we import this late, otherwise the whole monetdbe project is unimportable
        # if we don't have access to monetdbe shared library
        from monetdbe._cffi.convert import make_string, monet_c_type_map
        from monetdbe._cffi.internal import result_fetch

        if not self.result:
            return

        columns = list(map(lambda x: result_fetch(self.result, x), range(self.result.ncols)))
        name = (make_string(rcol.name) for rcol in columns)
        type_code = (monet_c_type_map[rcol.type].sql_type for rcol in columns)
        display_size = repeat(None)
        internal_size = repeat(None)
        precision = repeat(None)
        scale = repeat(None)
        null_ok = repeat(None)
        descriptions = list(zip(name, type_code, display_size, internal_size, precision, scale, null_ok))
        return [Description(*i) for i in descriptions]

    def execute(
            self, query: str,
            args: parameters_type = None,
            cursor: Optional[Type['Cursor']] = None,
            paramstyle: str = "qmark"
    ) -> 'Cursor':
        """
        Execute a SQL query

        This is a nonstandard and SQLite compatible shortcut that creates a cursor object by calling the cursor()
        method, calls the cursor’s execute() method with the parameters given, and returns the cursor.

        Args:
            query: The SQL query to execute
            args:  The optional SQL query arguments
            cursor: An optional Cursor object
            paramstyle: The style of the args, can be qmark, numeric, format or pyformat

        Returns:
            A new cursor.
        """
        cur = self.cursor(factory=cursor).execute(query, args, paramstyle)
        self.consistent = True
        return cur

    def executemany(
            self,
            query: str,
            args_seq: Union[Iterator, Iterable[parameters_type]],
            cursor: Optional[Type['Cursor']] = None
    ) -> 'Cursor':
        """
        Prepare a database query and then execute it against all parameter sequences or mappings found in the
        sequence seq_of_parameters.

        This is a nonstandard and SQLite compatible shortcut that creates a cursor object by calling the cursor()
        method, calls the cursor’s execute() method with the parameters given, and returns the cursor.

        Args:
            query: The SQL query to execute
            args_seq:  The optional SQL query arguments
            cursor: A Cursor class

        Returns:
            A new cursor instance of the supplied cursor class
        """
        cur = self.cursor(factory=cursor)
        for args in args_seq:
            cur.execute(query, args)
        return cur

    def commit(self, *args, **kwargs) -> 'Cursor':
        self._check()
        return self.execute("COMMIT")

    def close(self, *args, **kwargs) -> None:
        if not hasattr(self, '_internal'):
            return

        if self._internal:
            self._internal.close()
        self._internal = None

    def cursor(self, factory: Optional[Type['Cursor']] = None) -> 'Cursor':
        """
        Create a new cursor.

        Args:
            factory: An optional factory. If supplied, this must be a callable returning an instance of Cursor or its
                     subclasses.

        Returns:
            a new cursor.
        """
        self._check()

        if not factory:
            from monetdbe.cursors import Cursor  # type: ignore[attr-defined]
            factory = Cursor

        cursor = factory(con=self)  # type: ignore[misc]
        if not cursor:
            raise TypeError

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
        self._check()
        return self._internal.in_transaction()

    def set_autocommit(self, value: bool) -> None:
        """
        Set the connection to auto-commit mode.

        Args:
            value: a boolean value
        """
        self._check()
        return self._internal.set_autocommit(value)  # type: ignore

    def read_csv(self, table, *args, **kwargs):
        return self.cursor().read_csv(table, *args, **kwargs)

    def write_csv(self, table, *args, **kwargs):
        return self.cursor().write_csv(table, *args, **kwargs)

    def cleanup_result(self):
        if self.result and self._internal:
            self._internal.cleanup_result(self.result)
            self.result = None

    def query(self, query: str, make_result: bool = False) -> Tuple[Optional[Any], int]:
        """
        Execute a query directly on the connection.

        You probably don't want to use this. usually you use a cursor to execute queries.
        """
        self._check()
        return self._internal.query(query, make_result)  # type: ignore[union-attr]

    def prepare(self, operation: str):
        self._check()
        return self._internal.prepare(operation)  # type: ignore[union-attr]

    def cleanup_statement(self, statement: str) -> None:
        self._check()
        self._internal.cleanup_statement(statement)  # type: ignore[union-attr]

    def append(self, table: str, data: Mapping[str, np.ndarray], schema: str = 'sys') -> None:
        self._check()
        self._internal.append(table, data, schema)  # type: ignore[union-attr]

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
