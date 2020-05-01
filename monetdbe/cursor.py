import typing

if typing.TYPE_CHECKING:
    from monetdbe.connection import Connection


class Cursor:
    lastrowid = 0

    @property
    def description(self):
        return []

    def __init__(self, connection: 'Connection'):
        self.connection = connection

    def execute(self, operation: str, parameters=None):
        return self.connection.execute(operation)

    def executemany(self, *args, **kwargs):
        return []

    def close(self, *args, **kwargs):
        ...

    def fetchall(self, *args, **kwargs):
        return []

    def fetchmany(self, *args, **kwargs):
        return []

    def fetchone(self, *args, **kwargs):
        return []

    def executescript(self, *args, **kwargs):
        return []
