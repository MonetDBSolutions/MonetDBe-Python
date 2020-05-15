from re import sub
from string import Formatter
from typing import Tuple, Optional, Iterable, Union, Dict, List, Any, Generator, Iterator
from warnings import warn

from monetdbe._cffi import extract
from monetdbe.connection import Connection
from monetdbe.exceptions import ProgrammingError, DatabaseError, OperationalError


def escape(v):
    return f"'{v}'"


class DefaultFormatter(Formatter):
    """
    This makes it possible to supply a dict with a __missing__() method (like a defaultdict)
    """

    def __init__(self, d: Dict):
        super().__init__()
        self.d = d

    def get_value(self, key, *args, **kwargs):
        s = self.d[key]
        if isinstance(s, str):
            return escape(s)
        else:
            return s


def format_query(query: str, parameters: Optional[Union[Iterable[str], Dict[str, Any]]] = None) -> str:
    if type(query) != str:
        raise TypeError

    if parameters is not None:
        if hasattr(type(parameters), '__getitem__') and hasattr(type(parameters), 'keys'):  # qmark style

            if '?' in query:
                raise ProgrammingError("'?' in formatting with qmark style parameters")

            # we ignore type below, since we already check if there is a keys method, but mypy doesn't undertand
            escaped = dict((k, escape(v)) if type(v) == str else (k, v) for k, v in parameters.items())  # type: ignore
            x = sub(r':(\w+)', r'{\1}', query)

            if hasattr(type(parameters), '__missing__'):
                # this is something like a dict with a default value
                try:
                    # mypy doesn't understand that this is a dict-like with a default __missing__ value
                    return DefaultFormatter(parameters).format(x, **escaped)  # type: ignore
                except KeyError as e:
                    raise ProgrammingError(e)
            try:
                return x.format(**escaped)
            except KeyError as e:
                raise ProgrammingError(e)
        elif hasattr(type(parameters), '__iter__'):  # named style

            if ':' in query:
                raise ProgrammingError("':' in formatting with named style parameters")

            # mypy gets confused here
            escaped = [f"'{i}'" if type(i) == str else i for i in parameters]  # type: ignore
            return query.replace('?', '{}').format(*escaped)
        else:
            raise ValueError(f"parameters '{parameters}' type '{type(parameters)}' not supported")
    else:
        # TODO: (gijs) this should probably be a bit more elaborate, support for escaping for example
        for symbol in ':?':
            if symbol in query:
                raise ProgrammingError(f"unexpected symbol '{symbol}' in operation")
        return query


class Cursor:
    lastrowid = 0

    def __init__(self, connection: 'Connection'):

        if not isinstance(connection, Connection):
            raise TypeError

        # changing array size has no effect for monetdbe
        self.arraysize = 1

        self.connection = connection
        self.result: Optional[Any] = None  # todo: maybe make a result python wrapper?
        self.rowcount = -1
        self.prepare_id: Optional[int] = None
        self._fetch_generator: Optional[Generator] = None
        self.description: Optional[Tuple[str]] = None

    def __iter__(self):
        columns = list(map(lambda x: self.connection.inter.result_fetch(self.result, x), range(self.result.ncols)))
        for r in range(self.result.nrows):
            if not self.description:
                # TODO (gijs): self.description = tuple(rcol.name for rcol in columns)
                self.description = tuple("TODO" for rcol in columns)
            row = tuple(extract(rcol, r) for rcol in columns)
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

        from re import sub, MULTILINE

        sql_script = sub('^\s*--.*\n?', '', sql_script, flags=MULTILINE)
        sql_script = sub('/\*.*\*/', '', sql_script, flags=MULTILINE)
        sql_script = sql_script.strip()

        for query in sql_script.split(';'):
            query = query.strip()
            if query:
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
