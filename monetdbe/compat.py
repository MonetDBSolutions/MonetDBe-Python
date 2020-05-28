"""
compatibility with MonetDBLite
"""
from warnings import warn

from monetdbe.dbapi2 import connect


def make_connection(*args, **kwargs):
    warn("make_connection() is deprecated and will be removed from future versions")
    return connect(*args, **kwargs)


make_connection.__doc__ = connect.__doc__


def shutdown():
    warn("shutdown() is deprecated and will be removed from future versions")


def init(_: str):
    warn("init() is deprecated and will be removed from future versions")

