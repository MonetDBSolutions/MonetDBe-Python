"""
compatibility with MonetDBLite
"""
from warnings import warn
from typing import List, Tuple
from pandas import DataFrame

from monetdbe.dbapi2 import connect
from monetdbe.cursor import Cursor
from monetdbe.connection import Connection


def make_connection(*args, **kwargs):
    warn("make_connection() is deprecated and will be removed from future versions")
    return connect(*args, **kwargs)


make_connection.__doc__ = connect.__doc__


def shutdown():
    warn("shutdown() is deprecated and will be removed from future versions")


def init(_: str):
    warn("init() is deprecated and will be removed from future versions")


def sql(query: str, client=None) -> DataFrame:
    warn("sql() is deprecated and will be removed from future versions")
    if client:
        if not isinstance(client, Connection):
            raise TypeError
        return client.execute(query).fetchdf()
    else:
        return connect().execute(query).fetchdf()


def create(table, values, schema=None, conn=None) -> Cursor:
    warn("create() is deprecated and will be removed from future versions")
    if not conn:
        conn = connect()
    return conn.cursor().create(table=table, values=values, schema=schema)


def insert(*args, **kwargs) -> Cursor:
    warn("insert() is deprecated and will be removed from future versions")
    if 'client' in kwargs:
        client = kwargs.pop('client')
        if not isinstance(client, Connection):
            raise TypeError
    else:
        client = connect()
    return client.cursor().insert(*args, **kwargs)
