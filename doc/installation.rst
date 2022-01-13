============
Installation
============

Binary wheel install (recommended)
==================================

you need:

 * An up-to-date Linux, OSX or Windows, running on a 64-bit Intel compatible x86 architecture
 * pip ``>= 19.3``
 * Python ``>= 3.10``

to make sure you have a recent pip first upgrade pip::

    $ pip install --upgrade pip

now you can install MonetDBe-Python with::

    $ pip install monetdbe

On supported platforms, this will download and install the binary wheel,
otherwise a source compile is started.


Source installation
===================

To compile MonetDBe-Python from source, you need to have MonetDB installed.
Download the latest MonetDB, or compile from source::

    $ hg clone https://dev.monetdb.org/hg/MonetDB
    $ cd MonetDB
    $ hg checkout default   # or any other branch, for example Jul2021
    $ mkdir build
    $ cd build
    $ cmake .. -DCMAKE_INSTALL_PREFIX=<monetdb_prefix> -DWITH_CRYPTO=OFF \
                -DPY3INTEGRATION=OFF -DCMAKE_BUILD_TYPE=Release -DASSERT=OFF
    $ make install


Don't forget to replace ``<monetdb_prefix>`` with where you want to have MonetDB
installed, for example ``/opt/monetdb``.

Now obtain the MonetDBe-Python source code from github::

    $ git clone https://github.com/MonetDBSolutions/MonetDBe-Python/
    $ cd MonetDBe-Python
    $ pip install .


If MonetDB is not installed in the default search paths (like ``/usr/local``),
you need to set some ``CFLAGS`` environment variables to have pip find MonetDB::

    $ CFLAGS="-I<monetdb_prefix>/include/ -L<monetdb_prefix>/lib" pip install .

By default, it is assumed you are compiling against the default branch of MonetDB.
If this is wrong, specify the correct branch by setting the ``MONETDB_BRANCH`` environment variable
before the ``pip install`` command above::

    $ MONETDB_BRANCH=Jul2021

If you set the library CFLAGS at compile time you probably also need to set ``LD_LIBRARY_PATH``
(or DYLD_LIBRARY_PATH on OS X)::

    $ LD_LIBRARY_PATH=<monetdb_prefix>/lib
