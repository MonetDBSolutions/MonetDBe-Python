# MonetDBe-Python

MonetDBe-Python - the Python embedded MonetDB

https://github.com/monetdBSolutions/MonetDBe-Python/

Full documentation: https://monetdbe.readthedocs.io/en/latest/


# requirements

For a binary wheel installation you need:

 * An up-to-date Linux, OSX or Windows
 * pip >= 19.3
 * Python >= 3.6

For a non-binary wheel installation you need to have
MonetDB installed, see the source installation section below.


# install

You can install monetdbe from pypi using:
```
$ pip install --upgrade pip
$ pip install monetdbe
```

On supported platforms, this will download and install the Binary wheel,
otherwise a source compile is started.


# usage

Just import and get started, no running a server required. Connecting without
an argument starts an in-memory storage instance:
```
from monetdbe import connect
con = connect()
```

See a simple example illustrating the Pandas support in this notebook:

https://github.com/MonetDBSolutions/MonetDBe-Python/blob/master/notebooks/basic_example.ipynb


# Source installation

See the detailed online installation documentation for instructions to build from source:

https://monetdbe.readthedocs.io/en/latest/installation.html#source-installation
