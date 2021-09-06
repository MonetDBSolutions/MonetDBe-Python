import numpy
import pytest
from shutil import rmtree
import monetdbe


@pytest.fixture(scope="function")
def monetdbe_empty_cursor(request, tmp_path):
    test_dbfarm = tmp_path.resolve().as_posix()
    connection = monetdbe.make_connection(test_dbfarm)

    def finalizer():
        if tmp_path.is_dir():
            connection.close()
            rmtree(test_dbfarm, ignore_errors=True)

    request.addfinalizer(finalizer)
    cursor = connection.cursor()
    return cursor


@pytest.fixture(scope="function")
def monetdbe_cursor(request, tmp_path):
    test_dbfarm = tmp_path.resolve().as_posix()

    connection = monetdbe.make_connection(test_dbfarm)

    def finalizer():
        if tmp_path.is_dir():
            connection.close()
            rmtree(test_dbfarm, ignore_errors=True)

    request.addfinalizer(finalizer)

    cursor = connection.cursor()
    cursor.create('integers', {'i': numpy.arange(10)})
    cursor.execute('INSERT INTO integers VALUES(NULL)')
    return cursor


@pytest.fixture(scope="function")
def monetdbe_cursor_autocommit(tmp_path):
    test_dbfarm = tmp_path.resolve().as_posix()
    connection = monetdbe.connect(test_dbfarm)

    connection.set_autocommit(True)
    cursor = connection.cursor()

    class Context:
        def __init__(self, cursor, connection, dbfarm):
            self.cursor = cursor
            self.connection = connection
            self.dbfarm = dbfarm

    context = Context(cursor, connection, test_dbfarm)

    yield context

    if tmp_path.is_dir():
        context.connection.close()
        rmtree(context.dbfarm, ignore_errors=True)


@pytest.fixture(scope="function")
def initialize_monetdbe(request, tmp_path):
    test_dbfarm = tmp_path.resolve().as_posix()
    connection = monetdbe.connect(test_dbfarm)

    def finalizer():
        if tmp_path.is_dir():
            connection.close()
            rmtree(test_dbfarm, ignore_errors=True)

    request.addfinalizer(finalizer)
    monetdbe.connect(test_dbfarm)
    return test_dbfarm
