from typing import Tuple, Optional, Iterable, Union, Any, Generator, Iterator
from collections import namedtuple
from warnings import warn
from monetdbe._cffi import extract, make_string
from monetdbe.connection import Connection
from monetdbe.exceptions import ProgrammingError, DatabaseError, OperationalError, Warning
from monetdbe.formatting import format_query, strip_split_and_clean


Description = namedtuple('Description', ('name', 'type_code', 'display_size', 'internal_size', 'precision', 'scale',
                                         'null_ok'))

class Cursor:
    lastrowid = 0

    def __init__(self, con: 'Connection'):

        if not isinstance(con, Connection):
            raise TypeError

        # changing array size has no effect for monetdbe
        self.arraysize = 1

        self.connection = con
        self.result: Optional[Any] = None  # todo: maybe make a result python wrapper?
        self.rowcount = -1
        self.prepare_id: Optional[int] = None
        self._fetch_generator: Optional[Generator] = None
        self.description: Optional[Tuple[str]] = None

    def __iter__(self):

        from itertools import repeat

        columns = list(map(lambda x: self.connection.inter.result_fetch(self.result, x), range(self.result.ncols)))
        for r in range(self.result.nrows):
            if not self.description:
                name = (make_string(rcol.name) for rcol in columns)
                type_code = (rcol.type for rcol in columns)
                display_size = repeat(None)
                internal_size = repeat(None)
                precision = repeat(None)
                scale = repeat(None)
                null_ok = repeat(None)

                self.description = Description._make(*list(zip(name, type_code, display_size, internal_size, precision, scale, null_ok)))

            row = tuple(extract(rcol, r, self.connection.text_factory) for rcol in columns)
            if self.connection.row_factory:
                yield self.connection.row_factory(cur=self, row=row)
            else:
                yield row

    def _check(self):
        if not self.connection or not self.connection.inter:
            raise ProgrammingError

    def execute(self, operation: str, parameters: Optional[Iterable] = None):
        self._check()
        self.description = None  # which will be set later in fetchall

        if self.result:
            self.connection.inter.cleanup_result(self.result)

        splitted = strip_split_and_clean(operation)
        if len(splitted) != 1:
            raise Warning("Multiple queries in one execute() call")

        formatted = format_query(operation, parameters)
        try:
            self.result, self.rowcount, self.prepare_id = self.connection.inter.query(formatted, make_result=True)
        except DatabaseError as e:
            raise OperationalError(e)
        self.connection.total_changes += self.rowcount
        return self

    def executemany(self, operation: str, seq_of_parameters: Union[Iterator, Iterable[Iterable]]):
        self._check()
        self.description = None  # which will be set later in fetchall

        if self.result:
            self.connection.inter.cleanup_result(self.result)

        total_affected_rows = 0

        if operation[:6].lower() == 'select':
            raise ProgrammingError("Don't use a SELECT statement with executemany()")

        if hasattr(seq_of_parameters, '__iter__'):
            iterator = iter(seq_of_parameters)
        else:
            iterator = seq_of_parameters  # type: ignore   # mypy gets confused here

        while True:
            try:
                parameters = next(iterator)
            except StopIteration:
                break

            formatted = format_query(operation, parameters)
            self.result, affected_rows, self.prepare_id = self.connection.inter.query(formatted, make_result=True)
            total_affected_rows += affected_rows

        self.rowcount = total_affected_rows
        self.connection.total_changes += total_affected_rows
        return self

    def close(self, *args, **kwargs):
        self.connection = None

    def fetchall(self):
        self._check()

        if not self.result:
            return []

        rows = [i for i in self]
        self.result = None
        return rows

    def fetchmany(self, size=None):
        self._check()

        if not self.result:
            return []

        if not size:
            size = self.arraysize
        if not self._fetch_generator:
            self._fetch_generator = self.__iter__()

        rows = []
        for i in range(size):
            try:
                rows.append(next(self._fetch_generator))
            except StopIteration:
                break
        return rows

    def fetchone(self, *args, **kwargs):
        self._check()

        if not self.result:
            return

        if not self._fetch_generator:
            self._fetch_generator = self.__iter__()
        try:
            return next(self._fetch_generator)
        except StopIteration:
            return None

    def executescript(self, sql_script: str):
        self._check()

        if not isinstance(sql_script, str):
            raise ValueError("script argument must be unicode.")

        for query in strip_split_and_clean(sql_script):
            self.execute(query)

    def create(self, table, values, schema=None):
        """
        Creates a table from a set of values or a pandas DataFrame.
        """
        # note: this is a backwards compatibility function with with monetdblite
        warn("set_autocommit() will be deprecated in future releases")
        self._check()
        raise NotImplemented

    def fetchnumpy(self):
        warn("fetchnumpy() will be deprecated in future releases")
        self._check()
        raise NotImplemented

    def fetchdf(self):
        warn("fetchdf() will be deprecated in future releases")
        self._check()
        raise NotImplemented

    def setoutputsize(self, *args, **kwargs):
        return

    def setinputsizes(self, *args, **kwargs):
        return
