import logging
from _warnings import warn
from pathlib import Path
from typing import Optional, Tuple, Any, Mapping, Iterator

import numpy as np
from monetdbe._lowlevel import ffi, lib

from monetdbe import exceptions
from monetdbe._cffi.convert import make_string, monet_numpy_map, extract, numpy_monetdb_map
from monetdbe._cffi.errors import check_error

_logger = logging.getLogger(__name__)


class Frontend:
    _active_context: Optional['Frontend'] = None
    in_memory_active: bool = False
    _connection: Optional[ffi.CData] = None

    def __init__(
            self,
            dbdir: Optional[Path] = None,
            memorylimit: int = 0,
            querytimeout: int = 0,
            sessiontimeout: int = 0,
            nr_threads: int = 0,
            have_hge: bool = False
    ):
        self.dbdir = dbdir
        self.memorylimit = memorylimit
        self.querytimeout = querytimeout
        self.sessiontimeout = sessiontimeout
        self.nr_threads = nr_threads
        self.have_hge = have_hge
        self._switch()

    @classmethod
    def set_active_context(cls, active_context: Optional['Frontend']):
        cls._active_context = active_context

    @classmethod
    def set_in_memory_active(cls, value: bool):
        cls.in_memory_active = value

    @classmethod
    def set_connection(cls, connection: Optional[ffi.CData]):
        cls._connection = connection

    def __del__(self):
        if self._active_context == self:
            # only close if we are deleting the active context
            self.close()

    def _switch(self):
        # todo (gijs): see issue #5
        # if not self.dbdir and self.in_memory_active:
        #    raise exceptions.NotSupportedError(
        #        "You can't open a new in-memory MonetDBe database while an old one is still open.")

        if self._active_context == self:
            return

        self.close()
        self.set_connection(self.open())
        self.set_active_context(self)

        if not self.dbdir:
            self.set_in_memory_active(True)

    def cleanup_result(self, result: ffi.CData):
        _logger.info("cleanup_result called")
        if result and self._connection:
            check_error(lib.monetdbe_cleanup_result(self._connection, result))

    def open(self):

        if not self.dbdir:
            url = ffi.NULL
        else:
            url = str(self.dbdir.resolve().absolute()).encode()

        p_connection = ffi.new("monetdbe_database *")

        p_options = ffi.new("monetdbe_options *")
        p_options.memorylimit = self.memorylimit
        p_options.querytimeout = self.querytimeout
        p_options.sessiontimeout = self.sessiontimeout
        p_options.nr_threads = self.nr_threads

        result_code = lib.monetdbe_open(p_connection, url, p_options)
        connection = p_connection[0]

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
        if self._connection:
            if lib.monetdbe_close(self._connection):
                raise exceptions.OperationalError("Failed to close database")
            self.set_connection(None)

        if self._active_context:
            self.set_active_context(None)

        if not self.dbdir:
            self.set_in_memory_active(True)

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
        if make_result:
            p_result = ffi.new("monetdbe_result **")
        else:
            p_result = ffi.NULL

        affected_rows = ffi.new("monetdbe_cnt *")
        check_error(lib.monetdbe_query(self._connection, query.encode(), p_result, affected_rows))

        if make_result:
            result = p_result[0]
        else:
            result = None

        return result, affected_rows[0]

    @staticmethod
    def result_fetch(result: ffi.CData, column: int) -> ffi.CData:
        p_rcol = ffi.new("monetdbe_column **")
        check_error(lib.monetdbe_result_fetch(result, p_rcol, column))
        return p_rcol[0]

    @staticmethod
    def result_fetch_numpy(monetdbe_result: ffi.CData) -> Mapping[str, np.ma.MaskedArray]:

        result = {}
        for c in range(monetdbe_result.ncols):
            rcol = Frontend.result_fetch(monetdbe_result, c)
            name = make_string(rcol.name)
            cast_string, cast_function, numpy_type, monetdbe_null = monet_numpy_map[rcol.type]

            # for non float/int we for now first make a numpy object array which we then convert to the right numpy type
            if numpy_type.type == np.object_:
                np_col: np.ndarray = np.array([extract(rcol, r) for r in range(monetdbe_result.nrows)])
                if rcol.type == lib.monetdbe_str:
                    np_col = np_col.astype(str)
                elif rcol.type == lib.monetdbe_date:
                    np_col = np_col.astype('datetime64[D]')  # type: ignore
                elif rcol.type == lib.monetdbe_time:
                    warn("Not converting column with type column since no proper numpy equivalent")
                elif rcol.type == lib.monetdbe_timestamp:
                    np_col = np_col.astype('datetime64[ns]')  # type: ignore
            else:
                buffer_size = monetdbe_result.nrows * numpy_type.itemsize  # type: ignore
                c_buffer = ffi.buffer(rcol.data, buffer_size)
                np_col = np.frombuffer(c_buffer, dtype=numpy_type)  # type: ignore

            if monetdbe_null:
                mask = np_col == monetdbe_null
            else:
                mask = np.ma.nomask  # type: ignore

            masked = np.ma.masked_array(np_col, mask=mask)

            result[name] = masked
        return result

    def set_autocommit(self, value: bool) -> None:
        check_error(lib.monetdbe_set_autocommit(self._connection, int(value)))

    @staticmethod
    def get_autocommit() -> bool:
        value = ffi.new("int *")
        check_error(lib.monetdbe_get_autocommit(value))
        return bool(value[0])

    def in_transaction(self) -> bool:
        return bool(lib.monetdbe_in_transaction(self._connection))

    def append(self, table: str, data: Mapping[str, np.ndarray], schema: str = 'sys') -> None:
        """
        Directly append an array structure
        """
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
            work_type_string, work_type = numpy_monetdb_map(column_values.dtype)
            if not work_type == existing_type:
                existing_type_string = monet_numpy_map[existing_type][0]
                error = f"Type '{work_type_string}' for appended column '{column_name}' " \
                        f"does not match table type '{existing_type_string}'"
                raise exceptions.ProgrammingError(error)
            work_column.type = work_type
            work_column.count = column_values.shape[0]
            work_column.name = ffi.new('char[]', column_name.encode())
            work_column.data = ffi.cast(f"{work_type_string} *", ffi.from_buffer(column_values))
            work_columns[column_num] = work_column
            work_objs.append(work_column)
        check_error(lib.monetdbe_append(self._connection, schema.encode(), table.encode(), work_columns, n_columns))

    def prepare(self, query):
        # todo (gijs): use :)
        stmt = ffi.new("monetdbe_statement **")
        lib.monetdbe_prepare(self._connection, query.encode(), stmt)
        return stmt[0]

    def bind(self, statement, data, parameter_nr):
        ...
        # todo (gijs): use :)
        #     extern char* monetdbe_bind(monetdbe_statement *stmt, void *data, size_t parameter_nr);

    def execute(self, statement):
        ...
        # todo (gijs): use :)
        # extern char* monetdbe_execute(monetdbe_statement *stmt, monetdbe_result **result, monetdbe_cnt* affected_rows);

    def cleanup_statement(self, statement):
        ...
        # todo (gijs): use :)
        # extern char* monetdbe_cleanup_statement(monetdbe_database dbhdl, monetdbe_statement *stmt);

    def dump_database(self, backupfile: Path):
        # todo (gijs): use :)
        lib.monetdbe_dump_database(self._connection, str(backupfile).encode())

    def dump_table(self, schema_name: str, table_name: str, backupfile: Path):
        # todo (gijs): use :)
        lib.monetdbe_dump_table(self._connection, schema_name.encode(), table_name.encode(), str(backupfile).encode())

    def get_columns(self, table: str, schema: str = 'sys') -> Iterator[Tuple[str, int]]:
        count_p = ffi.new('size_t *')
        names_p = ffi.new('char ***')
        types_p = ffi.new('int **')

        lib.monetdbe_get_columns(self._connection, schema.encode(), table.encode(), count_p, names_p, types_p)

        for i in range(count_p[0]):
            name = ffi.string(names_p[0][i]).decode()
            type_ = types_p[0][i]
            yield name, type_
