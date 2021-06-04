import logging
from _warnings import warn
from pathlib import Path
from typing import Optional, Tuple, Any, Mapping, Iterator, Dict, TYPE_CHECKING

import numpy as np
from monetdbe._lowlevel import ffi, lib

from monetdbe import exceptions
from monetdbe._cffi.convert import make_string, monet_c_type_map, extract, numpy_monetdb_map
from monetdbe._cffi.convert.bind import prepare_bind
from monetdbe._cffi.errors import check_error
from monetdbe._cffi.types_ import monetdbe_result, monetdbe_database, monetdbe_column, monetdbe_statement

if TYPE_CHECKING:
    from monetdbe.connection import Connection

_logger = logging.getLogger(__name__)


def result_fetch(result: monetdbe_result, column: int) -> monetdbe_column:
    p_rcol = ffi.new("monetdbe_column **")
    check_error(lib.monetdbe_result_fetch(result, p_rcol, column))
    return p_rcol[0]


def result_fetch_numpy(result: monetdbe_result) -> Mapping[str, np.ndarray]:
    result_dict: Dict[str, np.ndarray] = {}
    for c in range(result.ncols):
        rcol = result_fetch(result, c)
        name = make_string(rcol.name)
        type_info = monet_c_type_map[rcol.type]

        # for non float/int we for now first make a numpy object array which we then convert to the right numpy type
        if type_info.numpy_type.type == np.object_:
            np_col: np.ndarray = np.array([extract(rcol, r) for r in range(result.nrows)])
            if rcol.type == lib.monetdbe_str:
                np_col = np_col.astype(str)
            elif rcol.type == lib.monetdbe_date:
                np_col = np_col.astype('datetime64[D]')  # type: ignore
            elif rcol.type == lib.monetdbe_time:
                warn("Not converting column with type column since no proper numpy equivalent")
            elif rcol.type == lib.monetdbe_timestamp:
                np_col = np_col.astype('datetime64[ns]')  # type: ignore
        else:
            buffer_size = result.nrows * type_info.numpy_type.itemsize  # type: ignore
            c_buffer = ffi.buffer(rcol.data, buffer_size)
            np_col = np.frombuffer(c_buffer, dtype=type_info.numpy_type)  # type: ignore

        if type_info.null_value:
            mask = np_col == type_info.null_value
        else:
            mask = np.ma.nomask  # type: ignore[attr-defined]

        masked = np.ma.masked_array(np_col, mask=mask)

        result_dict[name] = masked
    return result_dict


def get_autocommit() -> bool:
    value = ffi.new("int *")
    check_error(lib.monetdbe_get_autocommit(value))
    return bool(value[0])


def bind(statement: monetdbe_statement, data: Any, parameter_nr: int) -> None:
    prepared = prepare_bind(data)
    check_error(lib.monetdbe_bind(statement, prepared, parameter_nr))


def execute(statement: monetdbe_statement, make_result: bool = False) -> Tuple[monetdbe_result, int]:
    if make_result:
        p_result = ffi.new("monetdbe_result **")
    else:
        p_result = ffi.NULL

    affected_rows = ffi.new("monetdbe_cnt *")
    check_error(lib.monetdbe_execute(statement, p_result, affected_rows))

    if make_result:
        result = p_result[0]
    else:
        result = None

    return result, affected_rows[0]


def version() -> str:
    return ffi.string(lib.monetdbe_version()).decode()


class Internal:
    _active_context: Optional['Internal'] = None
    _active_connection: Optional['Connection'] = None
    _monetdbe_database: Optional[monetdbe_database] = None

    def __init__(
            self,
            connection: "Connection",
            dbdir: Optional[Path] = None,
            memorylimit: int = 0,
            querytimeout: int = 0,
            sessiontimeout: int = 0,
            nr_threads: int = 0,
            have_hge: bool = False
    ):
        self._connection = connection
        self.dbdir = dbdir
        self.memorylimit = memorylimit
        self.querytimeout = querytimeout
        self.sessiontimeout = sessiontimeout
        self.nr_threads = nr_threads
        self.have_hge = have_hge
        self._switch()

    @classmethod
    def set_active_context(cls, active_context: Optional['Internal']):
        cls._active_context = active_context

    @classmethod
    def set_active_connection(cls, active_connection: Optional['Connection']):
        cls._active_connection = active_connection

    @classmethod
    def set_monetdbe_database(cls, connection: Optional[monetdbe_database]):
        cls._monetdbe_database = connection

    def __del__(self):
        if self._active_context == self:
            # only close if we are deleting the active context
            self.close()

    def _switch(self):
        if self._active_context == self:
            return

        # this is a bit scary but just to make sure the previous connection
        # can't touch us anymore
        if self._active_connection:
            self._active_connection._internal = None

        self.close()
        self.set_monetdbe_database(self.open())
        self.set_active_context(self)
        self.set_active_connection(self._connection)

    def cleanup_result(self, result: monetdbe_result):
        _logger.info("cleanup_result called")
        if result and self._monetdbe_database:
            check_error(lib.monetdbe_cleanup_result(self._monetdbe_database, result))

    def open(self) -> monetdbe_database:

        if not self.dbdir:
            url = ffi.NULL
        else:
            url = str(self.dbdir.resolve().absolute()).encode()

        p_monetdbe_database = ffi.new("monetdbe_database *")

        p_options = ffi.new("monetdbe_options *")
        p_options.memorylimit = self.memorylimit
        p_options.querytimeout = self.querytimeout
        p_options.sessiontimeout = self.sessiontimeout
        p_options.nr_threads = self.nr_threads

        result_code = lib.monetdbe_open(p_monetdbe_database, url, p_options)
        connection = p_monetdbe_database[0]

        errors = {
            0: "OK",
            -1: "Allocation failed",
            -2: "Error in DB",
        }

        if result_code:
            if result_code == -2:
                error = ffi.string(lib.monetdbe_error(connection)).decode()
                lib.monetdbe_close(connection)
            else:
                error = errors.get(result_code, "unknown error")
            raise exceptions.OperationalError(f"Failed to open database: {error} (code {result_code})")

        return connection

    def close(self) -> None:
        if self._monetdbe_database:
            if lib.monetdbe_close(self._monetdbe_database):
                raise exceptions.OperationalError("Failed to close database")
            self.set_monetdbe_database(None)

        if self._active_context:
            self.set_active_context(None)

        self.set_active_connection(None)

    def query(self, query: str, make_result: bool = False) -> Tuple[Optional[Any], int]:
        """
        Execute a query.

        Args:
            query: the query
            make_result: Create and return a result object. If enabled, you need to call cleanup_result on the
                          result afterwards

        returns:
            result, affected_rows

        """
        self._switch()
        if make_result:
            p_result = ffi.new("monetdbe_result **")
        else:
            p_result = ffi.NULL

        affected_rows = ffi.new("monetdbe_cnt *")
        check_error(lib.monetdbe_query(self._monetdbe_database, query.encode(), p_result, affected_rows))

        if make_result:
            result = p_result[0]
        else:
            result = None

        return result, affected_rows[0]

    def set_autocommit(self, value: bool) -> None:
        self._switch()
        check_error(lib.monetdbe_set_autocommit(self._monetdbe_database, int(value)))

    def in_transaction(self) -> bool:
        self._switch()
        return bool(lib.monetdbe_in_transaction(self._monetdbe_database))

    def append(self, table: str, data: Mapping[str, np.ndarray], schema: str = 'sys') -> None:
        """
        Directly append an array structure
        """
        self._switch()
        n_columns = len(data)
        existing_columns = list(self.get_columns(schema=schema, table=table))
        existing_names, existing_types = zip(*existing_columns)
        if not set(existing_names) == set(data.keys()):
            error = f"Appended column names ({', '.join(str(i) for i in data.keys())}) " \
                    f"don't match existing column names ({', '.join(existing_names)})"
            raise exceptions.ProgrammingError(error)

        work_columns = ffi.new(f'monetdbe_column * [{n_columns}]')
        work_objs = []
        for column_num, (column_name, existing_type) in enumerate(existing_columns):
            column_values = data[column_name]
            work_column = ffi.new('monetdbe_column *')
            type_info = numpy_monetdb_map(column_values.dtype)
            if not type_info.c_type == existing_type:
                existing_type_string = monet_c_type_map[existing_type].c_string_type
                error = f"Type '{type_info.c_string_type}' for appended column '{column_name}' " \
                        f"does not match table type '{existing_type_string}'"
                raise exceptions.ProgrammingError(error)
            work_column.type = type_info.c_type
            work_column.count = column_values.shape[0]
            work_column.name = ffi.new('char[]', column_name.encode())
            work_column.data = ffi.cast(f"{type_info.c_string_type} *", ffi.from_buffer(column_values))
            work_columns[column_num] = work_column
            work_objs.append(work_column)
        check_error(lib.monetdbe_append(self._monetdbe_database, schema.encode(), table.encode(), work_columns, n_columns))

    def prepare(self, query: str) -> monetdbe_statement:
        self._switch()
        stmt = ffi.new("monetdbe_statement **")
        check_error(lib.monetdbe_prepare(self._monetdbe_database, str(query).encode(), stmt))
        return stmt[0]

    def cleanup_statement(self, statement: monetdbe_statement) -> None:
        self._switch()
        lib.monetdbe_cleanup_statement(self._monetdbe_database, statement)

    def dump_database(self, backupfile: Path):
        # todo (gijs): use :)
        lib.monetdbe_dump_database(self._monetdbe_database, str(backupfile).encode())

    def dump_table(self, schema_name: str, table_name: str, backupfile: Path):
        # todo (gijs): use :)
        lib.monetdbe_dump_table(self._monetdbe_database, schema_name.encode(), table_name.encode(), str(backupfile).encode())

    def get_columns(self, table: str, schema: str = 'sys') -> Iterator[Tuple[str, int]]:
        self._switch()
        count_p = ffi.new('size_t *')
        names_p = ffi.new('char ***')
        types_p = ffi.new('int **')

        lib.monetdbe_get_columns(self._monetdbe_database, schema.encode(), table.encode(), count_p, names_p, types_p)

        for i in range(count_p[0]):
            name = ffi.string(names_p[0][i]).decode()
            type_ = types_p[0][i]
            yield name, type_
