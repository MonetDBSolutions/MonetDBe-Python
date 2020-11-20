=====================
Developer information
=====================


Setting up a testing environment
================================

For development it is recommended to set up a virtual environment inside the source folder:

.. code-block::

    $ python3 -m venv venv
    $ source python3/bin/activate

The last command will active the virtual environment, and will replace the python3 and pip commands
in your shell. Now make sure you have the latest pip installed:

.. code-block::

    $ pip install --upgrade pip

Now install the MonetDBe-Python project in developing mode (hence the -e):

.. code-block::

    $ CFLAGS="-I<monetdb_prefix>/include/ -L<monetdb_prefix>/lib/" pip install -e ".[test,doc]

The CFLAGS above are required to make sure pip can find MonetDB. Using developer mode, any changes to
the Python code will be directly reflected without re-installation. The only exception is code related
to the low-level interface, which does require a reinstall (just run the above command again).


Running the test suite
======================

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

    $ make docker-wheels
    $ venv/bin/pip install twine
    $ venv/bin/twine upload dist/*.whl dist/*.tar.gz



Making binary wheel for OSX
===========================

1. get a High Sierra machine (10.13)


2. install homebrew

.. code-block::

    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install.sh)"

4. Run the OSX wheel script

.. code-block::

   scripts/osx_wheel.sh


10 upload the wheels

.. code-block::

    pip install twine
    twine upload dist/*.whl


Making binary wheel for Windows
===============================


Compile MonetDB on Windows
--------------------------

1. install microsoft visual studio community edition:

https://visualstudio.microsoft.com/vs/community/


2. Refer to the Github Actions Windows build script `.github/workflows/windows.yml` for further actions.

