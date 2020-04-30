import logging
from monetdbe import exceptions

from monetdbe.inter.cffi import CFFIInterAPI

_logger = logging.getLogger(__name__)

logging.basicConfig(level=logging.INFO)

try:
    from _monetdbe_cffi import lib, ffi
except ImportError as e:
    _logger.error(e)
    _logger.error("try setting LD_LIBRARY_PATH to point to the location of libembedded.so")
    raise


def error(msg):
    if msg:
        _logger.error(msg)
        raise exceptions.DatabaseError(msg)


def main():
    inter = CFFIInterAPI()
    inter.startup()
    conn = inter.connect()

    inter.query(conn, "CREATE TABLE test (x integer, y string)")
    inter.query(conn, "INSERT INTO test VALUES (42, 'Hello'), (NULL, 'World')")
    result, affected_rows, prepare_id = inter.query(conn, "SELECT x, y FROM test; ", make_result=True)

    _logger.info(f"Query result with {result.ncols} cols and {result.nrows} rows")

    p_rcol = ffi.new("monetdb_column **")
    for r in range(result.nrows):
        for c in range(result.ncols):
            err = lib.monetdb_result_fetch(conn, p_rcol, result, c)
            error(err)
            rcol = p_rcol[0]

            if rcol.type == lib.monetdb_int32_t:
                col = ffi.cast("monetdb_column_int32_t *", rcol)
                if col.data[r] == col.null_value:
                    _logger.info("NULL")
                else:
                    _logger.info("%d" % col.data[r])

            if rcol.type == lib.monetdb_str:
                col = ffi.cast("monetdb_column_str *", rcol)
                if col.is_null(col.data[r]):
                    _logger.info("NULL")
                else:
                    _logger.info("%s" % ffi.string(col.data[r]))

    inter.cleanup_result(conn, result)
    inter.disconnect(conn)
    inter.shutdown()


if __name__ == '__main__':
    main()
