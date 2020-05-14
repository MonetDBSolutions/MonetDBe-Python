# monetdbe
MonetDBe - the Python embedded MonetDB

https://github.com/monetdBSolutions/MonetDBe-Python/

# requirements

For binary wheel installation you need:

 * Linux
 * pip >= 19.3
 * Python >= 3.6

For non-binary wheel installation (Windows, OSX) you also (for now) need to
have MonetDB installed.


# install

you can install monetdbe from pypi using:
```
# pip install monetdbe
```

On supported platforms, this will download and install the Binary wheel, otherwise a source compile is started.

# compile

You can also compile monetdbe from the source folder:
```
$ git clone https://github.com/MonetDBSolutions/MonetDBe-Python/
$ cd MonetDBe-Python
$ pip install .
```

You need to have MonetDB available on the default search paths, if it is
installed in a different location you need to specify `CFLAGS`:
```
CFLAGS="-I<monetdb_prefix>/include/monetdb -I<monetdb_prefix>/lib/monetdb" pip install .
```
 
# development

![Python package](https://github.com/monetdBSolutions/MonetDBe-Python//workflows/Python%20package/badge.svg)


You can use pytest to run the test suite from the source checkout:
```
$ python3 -m venv venv
$ venv/bin/pip install -e .
$ venv/bin/pip install pytest
$ venv/bin/pytest
```

