=====================
Developer information
=====================


Setting up a testing environment
================================

For development it is recommended to set up a virtual environment inside the source folder:

.. code-block::

    $ python3 -m venv venv
    $ source python3/bin/activate

The last command will active the virtual environment, and will replace the python3 and pip commands in your shell. Now
make sure you have the latest pip installed:

.. code-block::

    $ pip install --upgrade pip

Now install the MonetDBe-Python project in developing mode (hence the -e):

.. code-block::

    $ CFLAGS="-I<monetdb_prefix>/include/ -L<monetdb_prefix>/lib/" pip install -e ".[test,doc]

The CFLAGS above are required to make sure pip can find MonetDB. Using developer mode, any changes to the Python code
will be directly reflected without reinstallation. The only exception is code related to the low-level interface, which
does require a reinstall (just run the above command again).


Running the teste suite
=======================

After setting up te testing environment, run from the source folder:

.. code-block::

    LD_LIBRARY_PATH=<monetdb_prefix>/lib pytest


Making binary wheel for Linux
=============================

requirements:
 * Docker
 * make

Then run

.. code-block::

    $ make wheels
    $ twine upload dist/*.whl dist/*.tar.gz



Making binary wheel for OSX
===========================



Making binary wheel for Windows
===============================


Compile MonetDB on Windows
--------------------------

install microsoft visual studio community edition:

https://visualstudio.microsoft.com/vs/community/

install bison:

http://gnuwin32.sourceforge.net/packages/bison.htm

install prce:

http://gnuwin32.sourceforge.net/packages/pcre.htm

Clone and build monetdb:

https://github.com/MonetDB/MonetDB


Compile monetdbe
----------------

