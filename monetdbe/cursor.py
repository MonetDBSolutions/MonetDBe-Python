from typing import TYPE_CHECKING, Tuple, Optional, Iterable, Any, Union, Dict
from re import sub
from warnings import warn
from monetdbe._cffi import extract, make_string
from monetdbe.exceptions import ProgrammingError, DatabaseError, OperationalError, Error
from monetdbe.connection import Connection


def format_query(query: str, parameters: Optional[Union[Tuple, Dict]] = None) -> str:
    if type(query) != str:
        raise TypeError

    if parameters is not None:
        if hasattr(type(parameters), '__getitem__') and hasattr(type(parameters), 'keys'):  # qmark style
            escaped = dict((k, f"'{v}'") if type(v) == str else (k, v) for k, v in parameters.items())
            x = sub(r':(\w+)', r'{\1}', query)
            try:
                return x.format(**escaped)
            except KeyError as e:
                raise ProgrammingError(e)
        elif hasattr(type(parameters), '__iter__'):  # named style
            escaped = [f"'{i}'" if type(i) == str else i for i in parameters]
            return query.replace('?', '{}').format(*escaped)
        else:
            raise ValueError(f"parameters '{parameters}' type '{type(parameters)}' not supported")
    else:
        return query


class Cursor:
    lastrowid = 0

    def __init__(self, connection: 'Connection'):

        if type(connection) != Connection:
            raise TypeError

        # changing array size has no effect for monetdbe
        self.arraysize = 1

        self.connection = connection
        self.result = None
        self.affected_rows = None
        self.prepare_id = None
        self._all = None
        self.description: Tuple[str] = tuple()

    def __iter__(self):
        return self.fetchone()

    def _check(self):
        if not self.connection or not self.connection.inter:
            raise ProgrammingError

    def execute(self, operation: str, parameters: Optional[Iterable] = None):
        self._check()
        self.description = None  # which will be set later in fetchall

        if self.result:
            self.connection.inter.cleanup_result(self.result)

        formatted = format_query(operation, parameters)
        try:
            self.result, self.affected_rows, self.prepare_id = self.connection.inter.query(formatted, make_result=True)
        except DatabaseError as e:
            raise OperationalError(e)
        return self

    def executemany(self, operation: str, parameters: Optional[Iterable] = None):
        self._check()
        self.description = None  # which will be set later in fetchall

        if self.result:
            self.connection.inter.cleanup_result(self.result)

        for param in parameters:
            formatted = format_query(operation, parameters)
            self.result, self.affected_rows, self.prepare_id = self.connection.inter.query(formatted, make_result=True)
        return self

    def close(self, *args, **kwargs):
        self.connection = None

    def fetchall(self):
        self._check()

        if not self.result:
            return

        columns = list(map(lambda x: self.connection.inter.result_fetch(self.result, x), range(self.result.ncols)))
        for r in range(self.result.nrows):
            if not self.description:
                # todo (gijs): make_string(rcol.name)
                self.description = tuple(rcol.name for rcol in columns)
            row = (extract(rcol, r) for rcol in columns)
            if self.connection.row_factory:
                yield self.connection.row_factory(cur=self, row=row)
            else:
                yield row

    def fetchmany(self, size=None):
        self._check()
        if not size:
            size = self.arraysize
        return [self.fetchone() for _ in range(size)]

    def fetchone(self, *args, **kwargs):
        self._check()
        if not self._all:
            self._all = self.fetchall()
        return next(self._all)

    def executescript(self, *args, **kwargs):
        self._check()
        raise NotImplemented

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
        raise NotImplemented

    def setinputsizes(self, *args, **kwargs):
        raise NotImplemented