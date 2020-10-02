"""
This module contains the CFFI code. It is a wrapper around the monetdbe shared library, converting
python calls and data into C and back.
"""
import logging
from pathlib import Path
from re import compile, DOTALL
from typing import Optional, Any, Dict, Tuple, Callable, List, Union
from warnings import warn
import numpy as np
from monetdbe import exceptions
from monetdbe.converters import converters
from monetdbe.pythonize import py_date, py_time, py_timestamp

_logger = logging.getLogger(__name__)

try:
    from monetdbe._lowlevel import lib, ffi
except ImportError as e:
    _logger.error(e)
    _logger.error("try setting LD_LIBRARY_PATH to point to the location of libmonetdbe.so")
    raise


def make_string(blob: ffi.CData) -> str:
    if blob:
        return ffi.string(blob).decode()
    else:
        return ""


def make_blob(blob: ffi.CData) -> str:
    if blob:
        return ffi.string(blob.data[0:blob.size])
    else:
        return ""


def py_float(data: ffi.CData) -> float:
    if 'FLOAT' in converters:
        return converters['FLOAT'](data)
    elif 'DOUBLE' in converters:
        return converters['DOUBLE'](data)
    else:
        return data


# MonetDB error codes
errors = {
    '2D000': exceptions.IntegrityError,  # COMMIT: failed
    '40000': exceptions.IntegrityError,  # DROP TABLE: FOREIGN KEY constraint violated
    '40002': exceptions.IntegrityError,  # INSERT INTO: UNIQUE constraint violated
    '42000': exceptions.OperationalError,  # SELECT: identifier 'asdf' unknown
    '42S02': exceptions.OperationalError,  # no such table
    'M0M29': exceptions.IntegrityError,  # The code monetdb emmitted before Jun2020
    '25001': exceptions.OperationalError,  # START TRANSACTION: cannot start a transaction within a transaction
}

error_match = compile(pattern=r"^(?P<exception_type>.*):(?P<namespace>.*):(?P<code>.*)!(?P<msg>.*)$", flags=DOTALL)


def check_error(msg: ffi.CData) -> None:
    """
    Raises:
         exceptions.Error: or subclass in case of error, which exception depends on the error type.
    """
    if msg:
        decoded = ffi.string(msg).decode()
        _logger.error(decoded)
        match = error_match.match(decoded)

        if not match:
            raise exceptions.OperationalError(decoded)

        _, _, error, msg = match.groups()

        if error not in errors:
            ...

        exception = errors.get(error, exceptions.DatabaseError)
        raise exception(msg)


#  monetdb C type, SQL type, numpy type, Cstringtype, pyconverter, null value, comment
mappings: List[Tuple[int, Optional[str], np.dtype, str, Optional[Callable], Optional[Union[int, float]]]] = [
    (lib.monetdbe_bool, "boolean", np.dtype(np.bool_), "bool", None, None),
    (lib.monetdbe_int8_t, "tinyint", np.dtype(np.int8), "int8_t", None, np.iinfo(np.int8).min),  # type: ignore
    (lib.monetdbe_int16_t, "smallint", np.dtype(np.int16), "int16_t", None, np.iinfo(np.int16).min),  # type: ignore
    (lib.monetdbe_int32_t, "int", np.dtype(np.int32), "int32_t", None, np.iinfo(np.int32).min),  # type: ignore
    (lib.monetdbe_int64_t, "bigint", np.dtype(np.int64), "int64_t", None, np.iinfo(np.int64).min),  # type: ignore
    (lib.monetdbe_size_t, None, np.dtype(np.uint64), "size_t", None, None),  # used by monetdb internally
    (lib.monetdbe_float, "real", np.dtype(np.float32), "float", py_float, np.finfo(np.float32).min),
    (lib.monetdbe_double, "float", np.dtype(np.float64), "double", py_float, np.finfo(np.float64).min),
    (lib.monetdbe_str, "string", np.dtype('=O'), "str", make_string, None),
    (lib.monetdbe_blob, "blob", np.dtype('=O'), "blob", make_blob, None),
    (lib.monetdbe_date, "date", np.dtype('=O'), "date", py_date, None),
    (lib.monetdbe_time, "time", np.dtype('=O'), "time", py_time, None),
    (lib.monetdbe_timestamp, "timestamp", np.dtype('=O'), "timestamp", py_timestamp, None),
]

numpy2monet_map = {numpy_type: (c_string, monet_type) for monet_type, _, numpy_type, c_string, _, _ in mappings}
monet_numpy_map = {monet_type: (c_string, converter, numpy_type, null_value) for
                   monet_type, _, numpy_type, c_string, converter, null_value in mappings}


def numpy_monetdb_map(numpy_type: np.dtype):
    if numpy_type.kind in ('i', 'f'):  # type: ignore
        return numpy2monet_map[numpy_type]
    raise exceptions.ProgrammingError("append() only support int and float family types")


def extract(rcol: ffi.CData, r: int, text_factory: Optional[Callable[[str], Any]] = None):
    """
    Extracts values from a monetdbe_column.

    The text_factory is optional, and wraps the value with a custom user supplied text function.
    """
    cast_string, cast_function, numpy_type, monetdbe_null = monet_numpy_map[rcol.type]
    col = ffi.cast(f"monetdbe_column_{cast_string} *", rcol)
    if col.is_null(col.data+r):
        return None
    else:
        if cast_function:
            result = cast_function(col.data[r])
            if rcol.type == lib.monetdbe_str and text_factory:
                return text_factory(result)
            else:
                return result
        else:
            return col.data[r]


class MonetEmbedded:
    _active_context: Optional['MonetEmbedded'] = None
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
    def set_active_context(cls, active_context: Optional['MonetEmbedded']):
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
            url = str(self.dbdir).encode()

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
            make_results: Create and return a result object. If enabled, you need to call cleanup_result on the
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
    def result_fetch(result: ffi.CData, column: int):
        p_rcol = ffi.new("monetdbe_column **")
        check_error(lib.monetdbe_result_fetch(result, p_rcol, column))
        return p_rcol[0]

    @staticmethod
    def result_fetch_numpy(monetdbe_result: ffi.CData):

        result = {}
        for c in range(monetdbe_result.ncols):
            rcol = MonetEmbedded.result_fetch(monetdbe_result, c)
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

    def set_autocommit(self, value: bool):
        check_error(lib.monetdbe_set_autocommit(self._connection, int(value)))

    @staticmethod
    def get_autocommit():
        value = ffi.new("int *")
        check_error(lib.monetdbe_get_autocommit(value))
        return value[0]

    def in_transaction(self) -> bool:
        return bool(lib.monetdbe_in_transaction(self._connection))

    def append(self, schema: str, table: str, data: Dict[str, np.ndarray]):
        """
        Directly apply an array structure
        """
        n_columns = len(data)
        monetdbe_columns = ffi.new(f'monetdbe_column * [{n_columns}]')

        for column_num, (column_name, column_values) in enumerate(data.items()):
            monetdbe_column = ffi.new('monetdbe_column *')

            monetdb_type_string, monetdb_type = numpy_monetdb_map(column_values.dtype)

            monetdbe_column.type = monetdb_type
            monetdbe_column.count = column_values.shape[0]
            monetdbe_column.name = ffi.new('char[]', column_name.encode())
            monetdbe_column.data = ffi.cast(f"{monetdb_type_string} *", ffi.from_buffer(column_values))
            monetdbe_columns[column_num] = monetdbe_column

        check_error(lib.monetdbe_append(self._connection, schema.encode(), table.encode(), monetdbe_columns, n_columns))

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

    def dump_table(self, schema_name, table_name, backupfile: Path):
        # todo (gijs): use :)
        lib.monetdbe_dump_table(self._connection, schema_name.encode(), table_name.encode(), str(backupfile).encode())
