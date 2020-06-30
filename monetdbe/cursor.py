from collections import namedtuple
from itertools import repeat
from typing import Tuple, Optional, Iterable, Union, Any, Generator, Iterator, List, Dict

import numpy as np
import pandas as pd

from monetdbe.connection import Connection
from monetdbe.exceptions import ProgrammingError, Warning, InterfaceError
from monetdbe.formatting import format_query, strip_split_and_clean
from monetdbe.monetize import monet_identifier_escape

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
        self.description: Optional[Description] = None
        self.row_factory = None

    def _set_description(self):
        self._columns = list(
            map(lambda x: self.connection.lowlevel.result_fetch(self.result, x), range(self.result.ncols)))

        # we import this late, otherwise the whole monetdbe project is unimportable if we don't have access to monetdbe.so
        from monetdbe._cffi import make_string

        name = (make_string(rcol.name) for rcol in self._columns)

        from monetdbe._cffi import type_map  # import here otherwise import cursor fails if module not compiled
        type_code = (type_map[rcol.type][2] for rcol in self._columns)

        display_size = repeat(None)
        internal_size = repeat(None)
        precision = repeat(None)
        scale = repeat(None)
        null_ok = repeat(None)

        descriptions = list(zip(name, type_code, display_size, internal_size, precision, scale, null_ok))
        self.description = [Description(*i) for i in descriptions]

    def __iter__(self):
        # we import this late, otherwise the whole monetdbe project is unimportable if we don't have access to monetdbe.so
        from monetdbe._cffi import extract

        columns = list(map(lambda x: self.connection.lowlevel.result_fetch(self.result, x), range(self.result.ncols)))
        for r in range(self.result.nrows):
            row = tuple(extract(rcol, r, self.connection.text_factory) for rcol in columns)
            if self.connection.row_factory:
                yield self.connection.row_factory(cur=self, row=row)
            elif self.row_factory:  # Sqlite backwards compatibly
                yield self.row_factory(self, row)
            else:
                yield row

    def fetchnumpy(self) -> np.ndarray:
        """
        Fetch all results and return a numpy array.

        like .fetchall(), but returns a numpy array.
        """
        self._check_connection()
        self._check_result()
        return self.connection.lowlevel.result_fetch_numpy(self.result)  # type: ignore

    def fetchdf(self) -> pd.DataFrame:
        """
        Fetch all results and return a Pandas DataFrame.

        like .fetchall(), but returns a Pandas DataFrame.
        """
        self._check_connection()
        self._check_result()
        return pd.DataFrame(self.fetchnumpy())

    def _check_connection(self) -> None:
        """
        Check if we are attached to the lower level interface

        Raises:
            ProgrammingError: if no lower level interface is attached
        """
        if not self.connection or not self.connection.lowlevel:
            raise ProgrammingError("no connection to lower level database available")

    def _check_result(self) -> None:
        """
        Check if an operation has been executed and a result is available.

        Raises:
            ProgrammingError: if no result is available.
        """
        if not self.result:
            raise ProgrammingError("fetching data but no query executed")

    def execute(self, operation: str, parameters: Optional[Iterable] = None) -> 'Cursor':
        """
        Execute operation

        Args:
            operation: the query you want to execute
            parameters: an optional iterable containing arguments for the operation.

        Returns:
            the cursor object itself

        Raises:
            OperationalError: if the execution failed
        """
        self._check_connection()
        self.description = None  # which will be set later in fetchall
        self._fetch_generator = None

        if self.result:
            self.connection.lowlevel.cleanup_result(self.result)  # type: ignore
            self.result = None

        splitted = strip_split_and_clean(operation)
        if len(splitted) == 0:
            raise ProgrammingError("Empty query")
        if len(splitted) > 1:
            raise ProgrammingError("Multiple queries in one execute() call")

        formatted = format_query(operation, parameters)
        self.result, self.rowcount = self.connection.lowlevel.query(formatted, make_result=True)  # type: ignore
        self.connection.total_changes += self.rowcount
        self._set_description()
        return self

    def executemany(self, operation: str, seq_of_parameters: Union[Iterator, Iterable[Iterable]]) -> 'Cursor':
        """
        Prepare a database operation (query or command) and then execute it against all parameter sequences or
        mappings found in the sequence seq_of_parameters.

        Args:
            operation: the SQL query to execute
            seq_of_parameters: An optional iterator or iterable containing an iterable of arguments
        """
        self._check_connection()
        self.description = None  # which will be set later in fetchall

        if self.result:
            self.connection.lowlevel.cleanup_result(self.result)  # type: ignore
            self.result = None

        total_affected_rows = 0

        if operation[:6].lower().strip() == 'select':
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
            self.result, affected_rows = self.connection.lowlevel.query(formatted, make_result=True)  # type: ignore
            total_affected_rows += affected_rows

        self.rowcount = total_affected_rows
        self.connection.total_changes += total_affected_rows
        self._set_description()
        return self

    def close(self, *args, **kwargs):
        """
        Shut down the connection.
        """
        self.connection = None

    def fetchall(self) -> List[Tuple]:
        """
        Fetch all (remaining) rows of a query result, returning them as a list of tuples).

        Returns:
            all (remaining) rows of a query result as a list of tuples

        Raises:
            Error: If the previous call to .execute*() did not produce any result set or no call was issued yet.
        """
        self._check_connection()

        # note (gijs): sqlite test suite doesn't want us to raise exception here, so for now I disable this
        # self._check_result()

        if not self.connection.consistent:
            raise InterfaceError("Tranaction rolled back, state inconsistent")

        if not self.result:
            return []

        rows = [i for i in self]
        self.result = None
        return rows

    def fetchmany(self, size=None):
        """
        Fetch the next set of rows of a query result, returning a list of tuples). An empty sequence is returned when
        no more rows are available.

        args:
            size: The number of rows to fetch. Fewer rows may be returned.

        Returns: A number of rows from a query result as a list of tuples

        Raises:
            Error: If the previous call to .execute*() did not produce any result set or no call was issued yet.

        """
        self._check_connection()
        # self._check_result() sqlite test suite doesn't want us to bail out

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

    def fetchone(self) -> Optional[Tuple]:
        """
        Fetch the next row of a query result set, returning a single tuple, or None when no more data is available.

        Returns:
            One row from a result set.

        Raises:
            Error: If the previous call to .execute*() did not produce any result set or no call was issued yet.

        """
        self._check_connection()
        # self._check_result() sqlite test suite doesn't want us to bail out

        if not self.result:
            return None

        if not self._fetch_generator:
            self._fetch_generator = self.__iter__()
        try:
            # todo (gijs): type
            return next(self._fetch_generator)  # type: ignore
        except StopIteration:
            return None

    def executescript(self, sql_script: str) -> None:
        """
        This is a nonstandard convenience and SQLite compatibility method for executing multiple SQL statements at once.
        It issues a COMMIT statement first, then executes the SQL script it gets as a parameter.

        Args:
            sql_script: A string containing one or more SQL statements, split by ;

        Raises:
            Error: If the previous call to .execute*() did not produce any result set or no call was issued yet.

        """
        self._check_connection()

        if not isinstance(sql_script, str):
            raise ValueError("script argument must be unicode.")

        for query in strip_split_and_clean(sql_script):
            self.execute(query)

    def create(self, table, values, schema=None):
        """
        Creates a table from a set of values or a pandas DataFrame.
        """
        # note: this is a backwards compatibility function with monetdblite
        self._check_connection()

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

    def insert(self, table: str, values: Union[pd.DataFrame, Dict[str, np.ndarray]], schema: str = 'sys'):
        """
        Inserts a set of values into the specified table.

        Args:
            table: The table to insert into
            values: The values. must be either a pandas DataFrame or a dictionary of values.
            schema: The SQL schema to use. If no schema is specified, the "sys" schema is used.
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

        column_names = values.keys()
        rows = values.values()

        columns = ", ".join(column_names)
        rows_zipped = list(zip(*rows))

        qmarks = ", ".join(['?'] * len(column_names))

        query = f"insert into {schema}.{table} ({columns}) values ({qmarks})"
        return self.executemany(query, rows_zipped)

        # todo (gijs): use a faster embedded backend to directly insert data, which should be much faster
        # return self.connection.inter.append(schema, table, values, column_count=len(values))

    def setoutputsize(self, *args, **kwargs) -> None:
        """
        This method would normally set a column buffer size for fetchion of large columns.

        MonetDBe-Python does not require this, so calling this function has no effect.
        """
        ...

    def setinputsizes(self, *args, **kwargs) -> None:
        """
        This method would normally be used before the .execute*() method is invoked to reserve memory.

        MonetDBe-Python does not require this, so calling this function has no effect.

        """
        ...

    def commit(self) -> 'Cursor':
        """
        Commit the current pending transaction.

        Returns:
            the current cursor
        """
        self.connection.commit()
        return self

    def transaction(self):
        """
        Start a new transaction

        Returns:
            the current cursor
        """
        return self.execute("BEGIN TRANSACTION")

    def scroll(self, count: int, mode: str = 'relative'):
        """
        Scroll the cursor in the result set to a new position according to mode.

        We dont support scrolling, since the full result is available.
        """
        raise NotImplementedError
