============
Introduction
============

Harnessing the power of a database server for data analytics into an embeddable library is the first step on the road to
benefit from its performance features. MonetDBe is the core of MonetDB, which is itself written in C. We started out with
a small C-API to build our first embedded applications.

However, the MonetDB eco system also provides APIs to Python, Java, Ruby, R, PhP… They all rely on the JDBC/ODBC layer
for interaction with the server. Such a bridge towards the embedded kernel is evidently not the way to go for all.

Therefore, our next target was to make the MonetDBe functionality available as a simple drop-in library in Python.
Python has a clearly defined database interface, called DB-API 2.0. Furthermore, with a claimed installed base of SQLite
of more than one billion there is a lot of code out there and users are used to its programmatic interface. The goal was
set to follow the Python/SQLite3 interface as much as possible.

We followed a test-driven approach by starting with the test suite for Python/SQLite 3 and working our way through all
the unit tests covered. The complete list is included in the .../tests directory. Several tests where skipped, because
they are too tightly coupled with the SQLite approach to database management. On the Github page you find a list 
of `open issues and the planning https://github.com/MonetDBSolutions/MonetDBe-Python/issues`  for the next milestones.

For example, the row factory functions are not supported. They coped with the limited set of data types
supported by SQLit, which triggers an (expensive) call back method when accessing the elements in 
a result set. MonetDBe has a much richer basic type system that includes e.g. the temporals, UUIDS, JSON ond DECIMAL out of the box.
Likewise, transaction management in MonetDBe is based on `MVCC https://www.monetdb.org/blog/optimistic-concurrency-control`
without explicit levels of isolations.  A remnant of the past when systems were based on explicit locking.

How does it work?
====================
Using the library starts with simply getting the module into your Python environment, ‘pip install monetdbe’:
A minimal example to see if everything works as expected:

```
    import monetdbe
    conn = monetdbe.connect(':memory:')
    c = conn.cursor()
    c.execute('SELECT count(*) FROM tables')
    print(c.fetchone())
```

Storage options
===============
One of the key factors in an embedded database system is the location of the persistent data, if it needs to persist.  In
MonetDBe we opted for a simple interface based on URLs, :memory:, /OSpath/directory, file://filename?withoptions, monetdb://mapi_host:port/db?withoptions. 
The benefit of this approach is that one can start developing the application with ':memory:' storage and switch to
the server version by simply changing the connection point.
The pre-release implementation of MonetDBe is limited to a single ':memory:' or a local directory.


And how about debugging and stability
=====================================

Using an embedded database library also comes with mutual responsibility. Unlike a server solution, your program could 
easily lead to a corrupted with peek/pook in the underlying database structures (using C functions).
For debugging you can rely on the logging scheme available in every MonetDBe instance or the Python logging module.

What are the caveats?
=====================

There are a few caveats to the approach presented. SQLite and MonetDBe do not align 100% on the same interpretation of
the SQL standard. MonetDBe is more strict. This may result in minor differences in error handling or even some surprises
in the results. An overview is provided in the `migrations <>` section.

REMINDER, the Python package monetdbe is an *alpha release* made available from PyPi. You don’t need to install MonetDB itself.
Several rough edges and features deemed urgent are being dealt with before MonetDBe becomes an official release, 
but users are more than welcome to try it out.
