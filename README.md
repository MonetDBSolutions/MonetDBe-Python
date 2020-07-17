# monetdbe
MonetDBe - the Python embedded MonetDB

https://github.com/monetdBSolutions/MonetDBe-Python/

documentation: https://monetdbe.readthedocs.io/en/latest/

# requirements

For binary wheel installation you need:

 * Linux or OSX 10.13+
 * pip >= 19.3
 * Python >= 3.6

For non-binary wheel installation (Windows) you also need to have MonetDB installed, see the source installation section below.


# install

you can install monetdbe from pypi using:
```
$ pip install --upgrade pip
$ pip install monetdbe
```

On supported platforms, this will download and install the Binary wheel, otherwise a source compile is started.


# usage

Just import and get started, no running a server required. Connecting without an argument starts an in-memory storage instance:
```
from monetdb import connect
con = connect()
```

See a simple example illustrating the Pandas support in this notebook:

https://github.com/MonetDBSolutions/MonetDBe-Python/blob/master/notebooks/basic_example.ipynb

# Source installation

see the detailed online installation documentation for instructions to build from source:

https://monetdbe.readthedocs.io/en/latest/installation.html#source-installation
