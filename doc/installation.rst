============
installation
============

Binary wheel install (recommended)
==================================

The recommended way to install MonetDBe-Python is using binary wheels distributed by pypi. For now, only OS X and Linux
are supported.

You need:

 * Linux or OSX 10.13+
 * pip >= 19.3
 * Python >= 3.6

For non-binary wheel installation (Windows) you also need to have MonetDB installed.

.. code-block::

    $ pip install monetdbe


On supported platforms, this will download and install the Binary wheel, otherwise a source compile is started.

Source installation
===================

To compile MonetDBe-Python from source, you need to have MonetDB installed. Download the latest MonetDB, or compile
from source. Make sure you have INT128 support enabled:

.. code-block::

    $ hg clone hg://dev.monetdb.org/hg/MonetDB
    $ cd MonetDB
    $ mkdir build
    $ cd build
    $ cmake .. -DCMAKE_INSTALL_PREFIX=<monetdb_prefix> -DINT128=ON
    $ make install


Don't forget to replace `<monetdb_prefix>` with where you want to have MonetDB installed, for example `/opt/monetdb`.

Now obtain the MonetDBe-Python source code from github:

.. code-block::

    $ git clone https://github.com/MonetDBSolutions/MonetDBe-Python/
    $ cd MonetDBe-Python
    $ pip install .


If MonetDB is not installed in the default search paths (like `/usr/local`), you need to set some `CFLAGS` environment
variables to have pip find MonetDB:

.. code-block::

    $ CFLAGS="-I<monetdb_prefix>/include/ -L<monetdb_prefix>/lib/monetdb" pip install .
