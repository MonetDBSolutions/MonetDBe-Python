from typing import Tuple, Optional, Iterable, Union, Any, Generator, Iterator
from collections import namedtuple
from itertools import repeat
from warnings import warn
import numpy as np
import pandas as pd
from monetdbe._cffi import extract, make_string
from monetdbe.monetize import monet_identifier_escape
from monetdbe.connection import Connection
from monetdbe.exceptions import ProgrammingError, DatabaseError, OperationalError, Warning
from monetdbe.formatting import format_query, strip_split_and_clean

Description = namedtuple('Description', ('name', 'type_code', 'display_size', 'internal_size', 'precision', 'scale',
                                         'null_ok'))


def __convert_pandas_to_numpy_dict__(df):
    if type(df) == pd.DataFrame:
        res = {}
        for tpl in df.to_dict().items():
            res[tpl[0]] = np.array(list(tpl[1].values()))
        return res
    return df


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

    def _set_description(self, columns):
        name = (make_string(rcol.name) for rcol in columns)
        type_code = (rcol.type for rcol in columns)
        display_size = repeat(None)
        internal_size = repeat(None)
        precision = repeat(None)
        scale = repeat(None)
        null_ok = repeat(None)
        self.description = Description._make(
            *list(zip(name, type_code, display_size, internal_size, precision, scale, null_ok)))

    def __iter__(self):
        columns = list(map(lambda x: self.connection.inter.result_fetch(self.result, x), range(self.result.ncols)))
        for r in range(self.result.nrows):
            if not self.description:
                self._set_description(columns)

            row = tuple(extract(rcol, r, self.connection.text_factory) for rcol in columns)
            if self.connection.row_factory:
                yield self.connection.row_factory(cur=self, row=row)
            else:
                yield row

    def fetchnumpy(self):
        self._check()
        return self.connection.inter.result_fetch_numpy(self.result)

    def fetchdf(self):
        self._check()
        return pd.DataFrame(self.fetchnumpy())

    def _check(self):
        if not self.connection or not self.connection.inter:
            raise ProgrammingError

    def execute(self, operation: str, parameters: Optional[Iterable] = None):
        self._check()
        self.description = None  # which will be set later in fetchall
        self._fetch_generator = None

        if self.result:
            self.connection.inter.cleanup_result(self.result)
            self.result = None

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
        """
        Prepare a database operation (query or command) and then execute it against all parameter sequences or
        mappings found in the sequence seq_of_parameters.
        """
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
        self._check()

        column_types = []

        if not isinstance(values, dict):
            values = __convert_pandas_to_numpy_dict__(values)
        else:
            vals = {}
            for tpl in values.items():
                if isinstance(tpl[1], np.ma.core.MaskedArray):
                    vals[tpl[0]] = tpl[1]
                else:
                    vals[tpl[0]] = np.array(tpl[1])
            values = vals
        if schema is None:
            schema = "sys"
        for key, value in values.items():
            arr = np.array(value)
            if arr.dtype == np.bool:
                column_type = "BOOLEAN"
            elif arr.dtype == np.int8:
                column_type = 'TINYINT'
            elif arr.dtype == np.int16 or arr.dtype == np.uint8:
                column_type = 'SMALLINT'
            elif arr.dtype == np.int32 or arr.dtype == np.uint16:
                column_type = 'INT'
            elif arr.dtype == np.int64 or arr.dtype == np.uint32 or arr.dtype == np.uint64:
                column_type = 'BIGINT'
            elif arr.dtype == np.float32:
                column_type = 'REAL'
            elif arr.dtype == np.float64:
                column_type = 'DOUBLE'
            elif np.issubdtype(arr.dtype, np.str_) or np.issubdtype(arr.dtype, np.unicode_):
                column_type = 'STRING'
            else:
                raise Exception('Unsupported dtype: %s' % (str(arr.dtype)))
            column_types.append(column_type)
        query = 'CREATE TABLE %s.%s (' % (
            monet_identifier_escape(schema), monet_identifier_escape(table))
        index = 0
        for key in values.keys():
            query += '%s %s, ' % (monet_identifier_escape(key), column_types[index])
            index += 1
        query = query[:-2] + ");"
        # create the table
        self.execute(query)
        # insert the data into the table
        self.insert(table, values, schema=schema)

    def insert(self, table, values, schema=None):
        """
        Inserts a set of values into the specified table.

        The values must be either a pandas DataFrame or a dictionary of values. If no schema is specified, the "sys"
        schema is used. If no client context is provided, the default client context is used.
           """

        if not isinstance(values, dict):
            values = __convert_pandas_to_numpy_dict__(values)
        else:
            vals = {}
            for tpl in values.items():
                if isinstance(tpl[1], np.ma.core.MaskedArray):
                    vals[tpl[0]] = tpl[1]
                else:
                    vals[tpl[0]] = np.array(tpl[1])
            values = vals

        for column, rows in values.items():
            self.executemany(f"insert into {table} ({column}) values (?)", ((i,) for i in rows))
        # return self.connection.inter.append(schema, table, values, column_count=len(values))

    def setoutputsize(self, *args, **kwargs):
        return

    def setinputsizes(self, *args, **kwargs):
        return

    def commit(self):
        self.connection.commit()
