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

1. get a High Sierra machine (10.13)


2. install homebrew

.. code-block::

    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install.sh)"

3. install requirements
.. code-block::

    brew install python3 bison cmake mercurial pyenv openssl

4.  get monetdb
.. code-block::

    hg clone hg://dev.monetdb.org/hg/MonetDB

5.  build monetdb
.. code-block::

    cd MonetDB
    mkdir build
    cd build
    cmake .. -DPY3INTEGRATION=OFF -DBISON_EXECUTABLE=/usr/local/opt/bison/bin/bison -DCMAKE_INSTALL_PREFIX=~/opt
    make -j10 install

6.  install the pythons
.. code-block::

    pyenv install 3.6.10
    pyenv install 3.7.7
    pyenv install 3.8.2

7.  set some flags to find the monetdb libs
.. code-block::

    export CFLAGS="-I/Users/gijs/opt/include -L/Users/gijs/opt/lib"
    export DYLD_LIBRARY_PATH=/Users/gijs/opt/lib

8. make the binary wheels
.. code-block::

    ~/.pyenv/versions/3.6.10/bin/python setup.py bdist_wheel
    ~/.pyenv/versions/3.7.7/bin/python setup.py bdist_wheel
    ~/.pyenv/versions/3.8.2/bin/python setup.py bdist_wheel

9 fix the binary wheels
.. code-block::

    ~/.pyenv/versions/3.8.2/bin/pip install delocate
    ~/.pyenv/versions/3.8.2/bin/delocate-wheel -v dist/*.whl

10 upload the wheels
.. code-block::

    ~/.pyenv/versions/3.8.2/bin/pip install twine
    ~/.pyenv/versions/3.8.2/bin/twine upload dist/*.whl




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

