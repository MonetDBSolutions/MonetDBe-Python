=====================
Developer information
=====================


Setting up a testing environment
================================

For development it is recommended to set up a virtual environment inside the source folder:

.. code-block::

    $ python3 -m venv venv
    $ source venv/bin/activate

The last command will active the virtual environment, and will replace the python3 and pip commands
in your shell. Now make sure you have the latest pip installed:

.. code-block::

    $ pip install --upgrade pip

Now install the MonetDBe-Python project in developing mode (hence the -e):

.. code-block::

    $ CFLAGS="-I<monetdb_prefix>/include/ -L<monetdb_prefix>/lib64/" pip install -e ".[test,doc]"

The CFLAGS above are required to make sure pip can find MonetDB. Using developer mode, any changes to
the Python code will be directly reflected without re-installation. The only exception is code related
to the low-level interface, which does require a reinstall (just run the above command again).


Running the test suite
======================

After setting up te testing environment, run from the source folder:

.. code-block::

    LD_LIBRARY_PATH=<monetdb_prefix>/lib pytest


Making binary wheels
====================

This is fully automated on Github Actions, the build scripts are located in `.github/workflows/`.

