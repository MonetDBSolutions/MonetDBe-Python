import numpy
import pytest
from shutil import rmtree
import monetdbe


@pytest.fixture(scope="function")
def monetdbe_empty_cursor(request, tmp_path):
    test_dbfarm = tmp_path.resolve().as_posix()

    def finalizer():
        if tmp_path.is_dir():
            monetdbe.connect(tmp_path).close()
            rmtree(test_dbfarm)

    request.addfinalizer(finalizer)
    connection = monetdbe.make_connection(test_dbfarm)
    cursor = connection.cursor()
    return cursor


@pytest.fixture(scope="function")
def monetdbe_cursor(request, tmp_path):
    test_dbfarm = tmp_path.resolve().as_posix()

    def finalizer():
        if tmp_path.is_dir():
            monetdbe.connect(tmp_path).close()
            rmtree(test_dbfarm)

    request.addfinalizer(finalizer)

    connection = monetdbe.make_connection(test_dbfarm)
    cursor = connection.cursor()
    cursor.create('integers', {'i': numpy.arange(10)})
    cursor.execute('INSERT INTO integers VALUES(NULL)')
    return cursor


@pytest.fixture(scope="function")
def monetdbe_cursor_autocommit(request, tmp_path):
    test_dbfarm = tmp_path.resolve().as_posix()

    def finalizer():
        if tmp_path.is_dir():
            monetdbe.connect(tmp_path).close()
            rmtree(test_dbfarm)

    request.addfinalizer(finalizer)
    connection = monetdbe.connect(test_dbfarm)
    connection.set_autocommit(True)
    cursor = connection.cursor()
    return cursor, connection, test_dbfarm


@pytest.fixture(scope="function")
def initialize_monetdbe(request, tmp_path):
    test_dbfarm = tmp_path.resolve().as_posix()

    def finalizer():
        if tmp_path.is_dir():
            monetdbe.connect(tmp_path).close()
            rmtree(test_dbfarm)

    request.addfinalizer(finalizer)
    monetdbe.connect(test_dbfarm)
    return test_dbfarm
