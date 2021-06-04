# type: ignore[union-attr]
from typing import Optional, Iterable, Union, cast, Iterator, Dict, Sequence, TYPE_CHECKING, Any, List, Mapping
from warnings import warn
import numpy as np
import pandas as pd
from monetdbe.connection import Connection, Description
from monetdbe.exceptions import ProgrammingError, InterfaceError
from monetdbe.formatting import format_query, strip_split_and_clean, parameters_type
from monetdbe.monetize import monet_identifier_escape, convert

if TYPE_CHECKING:
    from monetdbe.row import Row

paramstyles = {"qmark", "numeric", "named", "format", "pyformat"}


def _pandas_to_numpy_dict(df: pd.DataFrame) -> Dict[str, np.ndarray]:
    return {label: np.array(column) for label, column in df.iteritems()}  # type: ignore


class Cursor:
    lastrowid = 0

    def __init__(self, con: 'Connection'):

        if not isinstance(con, Connection):
            raise TypeError

        # changing array size has no effect for monetdbe
        self.arraysize = 1

        self.connection: Optional[Connection] = con
        self.rowcount = -1
        self.prepare_id: Optional[int] = None
        self.description: Optional[Description] = None
        self.row_factory = None

        self._fetch_generator: Optional[Iterator['Row']] = None

    def __del__(self):
        self.close()

    def _set_description(self):
        self.description = self.connection.get_description()

    def __iter__(self) -> Iterator[Union['Row', Sequence[Any]]]:
        # we import this late, otherwise the whole monetdbe project is unimportable
        # if we don't have access to monetdbe shared library
        from monetdbe._cffi.convert import extract
        from monetdbe._cffi.internal import result_fetch

        self._check_connection()

        if not self.connection.result:
            raise StopIteration

        columns = list(map(lambda x: result_fetch(self.connection.result, x),
                           range(self.connection.result.ncols)))  # type: ignore[union-attr]
        for r in range(self.connection.result.nrows):
            row = tuple(extract(rcol, r, self.connection.text_factory) for rcol in columns)
            if self.connection.row_factory:
                yield self.connection.row_factory(cur=self, row=row)
            elif self.row_factory:  # Sqlite backwards compatibly
                yield self.row_factory(self, row)
            else:
                yield row

    def _check_connection(self):
        """
        Check if we are attached to the lower level interface

        Raises:
            ProgrammingError: if no lower level interface is attached
        """
        if not hasattr(self, 'connection') or not self.connection:
            raise ProgrammingError("no connection to lower level database available")

    def _check_result(self) -> None:
        """
        Check if an operation has been executed and a result is available.

        Raises:
            ProgrammingError: if no result is available.
        """
        if not self.connection.result:
            raise ProgrammingError("fetching data but no query executed")

    def _execute_python(self, operation: str, parameters: parameters_type = None) -> 'Cursor':
        """
        Execute operation with Python based statement preparation.

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

        self.connection.cleanup_result()

        splitted = strip_split_and_clean(operation)
        if len(splitted) == 0:
            raise ProgrammingError("Empty query")
        if len(splitted) > 1:
            raise ProgrammingError("Multiple queries in one execute() call")

        formatted = format_query(operation, parameters)
        self.connection.result, self.rowcount = self.connection.query(formatted, make_result=True)
        self.connection.total_changes += self.rowcount
        self._set_description()
        return self

    def _execute_monetdbe(self, operation: str, parameters: parameters_type = None):
        from monetdbe._cffi.internal import bind, execute
        self._check_connection()
        statement = self.connection.prepare(operation)
        if parameters:
            for index, parameter in enumerate(parameters):
                bind(statement, parameter, index)
        self.connection.result, self.rowcount = execute(statement, make_result=True)
        self.connection.cleanup_statement(statement)
        self.connection.total_changes += self.rowcount
        self._set_description()
        return self

    def execute(
            self,
            operation: str,
            parameters: parameters_type = None,
            paramstyle: str = "qmark"
    ) -> 'Cursor':
        if paramstyle not in paramstyles:
            raise ValueError(f"Unknown paramstyle {paramstyle}")
        if (not parameters or isinstance(parameters, Sequence)) and paramstyle == "qmark":
            return self._execute_monetdbe(operation, parameters)
        return self._execute_python(operation, parameters)

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
        self.connection.cleanup_result()
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
            self.connection.result, affected_rows = self.connection.query(formatted, make_result=True)
            total_affected_rows += affected_rows

        self.rowcount = total_affected_rows
        self.connection.total_changes += total_affected_rows
        self._set_description()
        return self

    def close(self) -> None:
        """
        Shut down the connection.
        """
        if hasattr(self, 'connection') and self.connection and self.connection.result:
            self.connection.cleanup_result()
            self.connection.result = None
        self.connection = None

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
            values = _pandas_to_numpy_dict(values)
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
            if arr.dtype == np.bool_:
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
            elif np.issubdtype(arr.dtype, np.str_) or np.issubdtype(arr.dtype, np.unicode_) or np.issubdtype(arr.dtype,
                                                                                                             np.object_):
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
        return self

    def _insert_slow(self, table: str, data: Dict[str, np.ndarray], schema: str = 'sys'):
        column_names = data.keys()
        rows = data.values()
        columns = ", ".join([str(i) for i in column_names])
        rows_zipped = list(zip(*rows))
        qmarks = ", ".join(['?'] * len(column_names))
        query = f"insert into {schema}.{table} ({columns}) values ({qmarks})"
        return self.executemany(query, rows_zipped)

    def insert(self, table: str, values: Union[pd.DataFrame, Dict[str, np.ndarray]], schema: str = 'sys'):
        """
        Inserts a set of values into the specified table.

        Args:
            table: The table to insert into
            values: The values. must be either a pandas DataFrame or a dictionary of values.
            schema: The SQL schema to use. If no schema is specified, the "sys" schema is used.
       """
        if isinstance(values, pd.DataFrame):
            prepared = _pandas_to_numpy_dict(values)
        else:
            prepared = values

        for key, value in prepared.items():
            if not isinstance(value, (np.ma.core.MaskedArray, np.ndarray)):  # type: ignore
                prepared[key] = np.array(value)

        if sum(i.dtype.kind not in 'if' for i in prepared.values()):  # type: ignore
            warn(
                "One of the columns you are inserting is not of type int or float which fast append doesn't support. Falling back to regular insert.")
            return self._insert_slow(table, prepared, schema)
        return self.connection.append(schema=schema, table=table, data=prepared)

    def setoutputsize(self, *args, **kwargs) -> None:
        """
        This method would normally set a column buffer size for fetching of large columns.

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
        if not hasattr(self, 'connection') or not self.connection:
            raise ProgrammingError("no connection to lower level database available")

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

    def read_csv(self, table, *args, **kwargs):
        values = pd.read_csv(*args, **kwargs)
        return self.create(table=table, values=values)

    def fetchdf(self) -> pd.DataFrame:
        """
        Fetch all results and return a Pandas DataFrame.

        like .fetchall(), but returns a Pandas DataFrame.
        """
        self._check_connection()
        self._check_result()
        return pd.DataFrame(cast(pd.DataFrame, self.fetchnumpy()))  # cast to make mypy happy

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

        if not self.connection.result:
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

    def fetchone(self) -> Optional[Union['Row', Sequence]]:
        """
        Fetch the next row of a query result set, returning a single tuple, or None when no more data is available.

        Returns:
            One row from a result set.

        Raises:
            Error: If the previous call to .execute*() did not produce any result set or no call was issued yet.

        """
        self._check_connection()
        # self._check_result() sqlite test suite doesn't want us to bail out

        if not self.connection.result:
            return None

        if not self._fetch_generator:
            self._fetch_generator = self.__iter__()
        try:
            return next(self._fetch_generator)  # type: ignore[arg-type]
        except StopIteration:
            return None

    def write_csv(self, table, *args, **kwargs):
        return self.execute(f"select * from {table}").fetchdf().to_csv(*args, **kwargs)

    def __iter_numpy__(self) -> Iterator[Union['Row', Sequence[Any]]]:
        result = self.fetchall()

        for row in result:
            if self.connection.row_factory:  # type: ignore[union-attr]
                yield self.connection.row_factory(cur=self, row=tuple(row))  # type: ignore[union-attr]
            elif self.row_factory:  # Sqlite backwards compatibly
                yield self.row_factory(self, tuple(row))
            else:
                yield tuple(row)

    def fetchall(self) -> List[Union['Row', Sequence]]:
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

        if not self.connection.result:
            return []

        rows = [i for i in self]
        self.connection.result = None
        return rows

    def _fetchnumpy_slow(self) -> Mapping[str, np.ndarray]:
        self._check_connection()
        self._check_result()
        all_ = self.fetchall()
        names = (d.name for d in self.description)
        flipped = zip(*all_)
        return {k: v for k, v in zip(names, flipped)}

    def _fetchall_numpy(self):
        result = self.fetchnumpy()
        if result:
            return list(np.vstack(list(result.values())).T)
        return []

    def fetchnumpy(self) -> Mapping[str, np.ndarray]:
        """
        Fetch all results and return a numpy array.

        like .fetchall(), but returns a numpy array.
        """
        from monetdbe._cffi.internal import result_fetch_numpy

        self._check_connection()
        self._check_result()
        return result_fetch_numpy(self.connection.result)  # type: ignore[union-attr]
