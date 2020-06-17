"""
This module contains the CFFI code. It is a wrapper around the monetdbe embedded shared library, converting
python calls and data into C and back.
"""
import logging
from pathlib import Path
from re import compile, DOTALL
from typing import Optional, Any, Dict, Tuple, Callable, Type

import numpy as np

from monetdbe import exceptions
from monetdbe.converters import converters
from monetdbe.pythonize import py_date, py_time, py_timestamp

_logger = logging.getLogger(__name__)

try:
    from monetdbe._lowlevel import lib, ffi
except ImportError as e:
    _logger.error(e)
    _logger.error("try setting LD_LIBRARY_PATH to point to the location of libembedded.so")
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
    '2D000': exceptions.IntegrityError,    # COMMIT: failed
    '40000': exceptions.IntegrityError,    # DROP TABLE: FOREIGN KEY constraint violated
    '40002': exceptions.IntegrityError,    # INSERT INTO: UNIQUE constraint violated
    '42000': exceptions.OperationalError,  # SELECT: identifier 'asdf' unknown
    '42S02': exceptions.OperationalError,  # no such table
    'M0M29': exceptions.IntegrityError,    # The code monetdb emmitted before Jun2020
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
            raise exceptions.DatabaseError(decoded)

        _, _, error, msg = match.groups()

        if error not in errors:
            ...

        exception = errors.get(error, exceptions.DatabaseError)
        raise exception(msg)


# format: monetdb type: (cast name, converter function, numpy type, monetdb null value)
type_map: Dict[Any, Tuple[str, Optional[Callable], Optional[Type], Optional[Any]]] = {
    lib.monetdbe_bool: ("bool", bool, np.dtype(np.bool), None),
    lib.monetdbe_int8_t: ("int8_t", None, np.dtype(np.int8), np.iinfo(np.int8).min),
    lib.monetdbe_int16_t: ("int16_t", None, np.dtype(np.int16), np.iinfo(np.int16).min),
    lib.monetdbe_int32_t: ("int32_t", None, np.dtype(np.int32), np.iinfo(np.int32).min),
    lib.monetdbe_int64_t: ("int64_t", None, np.dtype(np.int64), np.iinfo(np.int64).min),
    lib.monetdbe_int128_t: ("int128_t", None, None, None),
    lib.monetdbe_size_t: ("size_t", None, None, None),
    lib.monetdbe_float: ("float", py_float, np.dtype(np.float), np.finfo(np.float).min),
    lib.monetdbe_double: ("double", py_float, np.dtype(np.float), np.finfo(np.float).min),
    lib.monetdbe_str: ("str", make_string, np.dtype(np.str), None),
    lib.monetdbe_blob: ("blob", make_blob, None, None),
    lib.monetdbe_date: ("date", py_date, np.dtype(np.datetime64), None),
    lib.monetdbe_time: ("time", py_time, np.dtype(np.datetime64), None),
    lib.monetdbe_timestamp: ("timestamp", py_timestamp, np.dtype(np.datetime64), None),
}


def extract(rcol, r: int, text_factory: Optional[Callable[[str], Any]] = None):
    """
    Extracts values from a monetdbe_column.

    The text_factory is optional, and wraps the value with a custom user supplied text function.
    """
    cast_string, cast_function, numpy_type, monetdbe_null = type_map[rcol.type]
    col = ffi.cast(f"monetdbe_column_{cast_string} *", rcol)
    if col.is_null(col.data[r]):
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


# Todo: workaround to get around the single embed instance limitation. can be class property also.
_active_python = None
_connection: Optional[ffi.CData] = None
in_memory_active = False


class MonetEmbedded:
    def __init__(self, dbdir: Optional[Path] = None):
        self.dbdir = dbdir
        self._switch()

    def __del__(self):
        self.close()

    def _switch(self):
        global _active_python, _connection, in_memory_active

        # todo (gijs): see issue #5
        # if not self.dbdir and in_memory_active:
        #    raise exceptions.NotSupportedError(
        #        "You can't open a new in-memory MonetDBe database while an old one is still open.")

        if _active_python == self:
            return

        self.close()
        _connection = self.open(self.dbdir)
        _active_python = self
        if not self.dbdir:
            in_memory_active = True

    def cleanup_result(self, result: ffi.CData):
        _logger.info("cleanup_result called")
        if result:
            check_error(lib.monetdbe_cleanup_result(_connection, result))

    def open(self, dbdir: Optional[Path] = None):
        if not dbdir:
            url = ffi.NULL
        else:
            url = str(dbdir).encode()  # ffi.new("char[]", str(dbdir).encode())

        p_connection = ffi.new("monetdbe_database *")
        p_options = ffi.new("monetdbe_options *")

        # options.memorylimit = ffi.NULL
        # options.nr_threads = ffi.NULL

        check_error(lib.monetdbe_open(p_connection, url, p_options))
        return p_connection[0]

    def close(self):
        _logger.info("close called")
        global _active_python, _connection, in_memory_active
        if _active_python:
            _active_python = None

        if _connection:
            check_error(lib.monetdbe_close(_connection))
            _connection = None

        if not self.dbdir:
            in_memory_active = False

    def query(self, query: str, make_result: bool = False) -> Tuple[Optional[Any], int]:
        """
        Execute a query.

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

        check_error(lib.monetdbe_query(_connection, query.encode(), p_result, affected_rows))

        if make_result:
            result = p_result[0]
        else:
            result = None

        return result, affected_rows[0]

    def result_fetch(self, result: ffi.CData, column: int):
        p_rcol = ffi.new("monetdbe_column **")
        check_error(lib.monetdbe_result_fetch(result, p_rcol, column))
        return p_rcol[0]

    def result_fetch_numpy(self, monetdbe_result: ffi.CData):

        result = {}
        for c in range(monetdbe_result.ncols):
            p_rcol = ffi.new("monetdbe_column **")
            check_error(lib.monetdbe_result_fetch(monetdbe_result, p_rcol, c))
            rcol = p_rcol[0]
            name = make_string(rcol.name)
            cast_string, cast_function, numpy_type, monetdbe_null = type_map[rcol.type]
            # todo (gijs): typing
            buffer_size = monetdbe_result.nrows * numpy_type.itemsize  # type: ignore
            c_buffer = ffi.buffer(rcol.data, buffer_size)
            np_col = np.frombuffer(c_buffer, dtype=numpy_type)

            if monetdbe_null:
                mask = np_col == monetdbe_null
                if mask.any():
                    masked = np.ma.masked_array(np_col, mask=mask)
                else:
                    masked = np_col
            else:
                masked = np_col

            result[name] = masked
        return result

    def set_autocommit(self, value: bool):
        check_error(lib.monetdbe_set_autocommit(_connection, int(value)))

    def get_autocommit(self):
        value = ffi.new("int *")
        check_error(lib.monetdbe_get_autocommit(value))
        return value[0]

    def in_transaction(self) -> bool:
        return bool(lib.monetdbe_in_transaction(_connection))

    def append(self, schema: str, table: str, batids, column_count: int):
        # todo (gijs): use :)
        check_error(lib.monetdbe_append(_connection, schema.encode(), table.encode(), batids, column_count))

    def prepare(self, query):
        # todo (gijs): use :)
        stmt = ffi.new("monetdbe_statement **")
        lib.monetdbe_prepare(_connection, query.encode(), stmt)
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
        lib.monetdbe_dump_database(_connection, str(backupfile).encode())

    def dump_table(self, schema_name, table_name, backupfile: Path):
        # todo (gijs): use :)
        lib.monetdbe_dump_table(_connection, schema_name.encode(), table_name.encode(), str(backupfile).encode())
