============
Introduction
============

Harnessing the power of a database server for data analytics into an embeddable library is the first step on the road to
benefit from its performance features. MonetDB/e is the core of MonetDB, which is itself written in C. We started out with
a small C-API to build our first embedded applications.

However, the MonetDB eco system also provides APIs to Python, Java, Ruby, R, PhP… They all rely on the JDBC/ODBC layer
for interaction with the server. Such a bridge towards the embedded kernel is evidently not the way to go.

Therefore, our next target was to make the MonetDB functionality available as a simple drop-in library in Python, called monetdbe.
Python has a clearly defined database interface, called DB-API 2.0. Furthermore, with a claimed installed base of SQLite
of more than one billion there is a lot of code out there and users are used to its programmatic interface. The goal was
set to follow the Python/SQLite3 interface as much as possible.

We followed a test-driven approach by starting with the test suite for Python/SQLite 3 and working our way through all
the unit tests covered. The complete list is included in the .../tests directory. Several tests where skipped, because
they are too tightly coupled with the SQLite approach to database management. We keep a list 
of `open issues <https://github.com/MonetDBSolutions/MonetDB/e-Python/issues>`_  and the planning for the next milestones.

For example, the row factory functions are not supported. They coped with the limited set of data types
supported by SQLite, which triggers an (expensive) call back method when accessing the elements in 
a result set. MonetDB/e has a much richer basic type system that includes e.g. the temporals, UUIDS, JSON ond DECIMAL out of the box.
Likewise, transaction management in MonetDB/e is based on `MVCC <https://www.monetdb.org/blog/optimistic-concurrency-control>`_
without explicit levels of isolations.  A remnant of the past when systems were based on explicit locking.

How does it work
================

Using the library starts with simply getting the module into your Python environment, ‘pip install monetdbe’.
A minimal example to see if everything works as expected::

    import monetdbe
    conn = monetdbe.connect(':memory:')
    c = conn.cursor()
    c.execute('SELECT count(*) FROM tables')
    print(c.fetchone())

A small collection of example programs can be found in the `monetdbe-examples <https://github.com/MonetDBSolutions/monetdbe-examples>`_ repository.

Storage options
===============
One of the key factors in an embedded database system is the location of the persistent data, if it needs to persist at all.  In
MonetDB/e we opted for a simple interface based on URLs, :memory:, /OSpath/directory, file://filename?withoptions, monetdb://mapi_host:port/db?withoptions. 
The benefit of this approach is that one can start developing the application with an in memory only, ':memory:', storage and switch to
the local directory or server version by simply changing the connection point.
The pre-release implementation of MonetDB/e is limited to a single ':memory:' or a local directory.


And how about debugging and stability
=====================================

Using an embedded database library also comes with mutual responsibility. Unlike a server solution, your program could 
easily lead to a corrupted database with peek/pook in the underlying database structures (using C-functions).
Such a corruption may be not immediately be detected. This can be countered by taking regular database backups.

For debugging you can rely on the logging scheme available in every MonetDB/e instance or the Python logging module.
Alternatively, the Python debugger gives information up to the point the code switches to the underlying C function.
Consider this a natural barrier not to cross, because the database kernel code is highly complex.

What are the caveats
====================

There are a few caveats to the approach presented. SQLite and MonetDB/e do not align 100% on the same interpretation of
the SQL standard. MonetDB/e is much more strict. This may result in minor differences in error handling or even some surprises
in the results. An overview is provided in the `Application Migration`_ section.

REMINDER, the Python package monetdbe is an *pre-release* made available from PyPi. You don’t need to install MonetDB itself.
Several rough edges and features deemed urgent are being dealt with before MonetDB/e becomes an official release, 
but users are more than welcome to try it out.
