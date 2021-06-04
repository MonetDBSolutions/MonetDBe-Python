
from typing import Dict
from logging import getLogger
from pprint import pprint

_logger = getLogger(__file__)


def get_info() -> Dict:
    """
    Fetch some MonetDBe specific properties
    """
    from monetdbe import connect
    from monetdbe._cffi.internal import version

    from_monetdb = connect().execute("select * from env()").fetchall()

    try:
        from monetdbe._cffi.branch import monetdb_branch
    except ImportError as e:
        _logger.error(f"can't import branch file: {e}")
        monetdb_branch = "not set"

    try:
        version_ = version()
    except Exception as e:
        _logger.error(f"can't call monetdb version() function: {e}")
        version_ = "not set"

    return {"from_monetdb": from_monetdb, "monetdb_branch": monetdb_branch, "version": version_}


def print_info():
    pprint(get_info())
