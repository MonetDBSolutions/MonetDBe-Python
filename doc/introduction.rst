============
introduction
============

What is the problem being addressed?
====================================

Harnessing the power of a database server for data analytics into an embeddable library is the first step on the road to
benefit from its performance features. MonetDBe is the core of MonetDB, which is itself written in C. We started out with
a small C-API to build our first embedded applications.

However, the MonetDB eco system also provides APIs to Python, Java, Ruby, R, PhP… They all rely on the JDBC/ODBC layer
for interaction with the server. Such a bridge towards the embedded kernel is evidently not the way to go for all.

Therefore, our next target was to make the MonetDBe functionality available as a simple drop-in library in Python.
Python has a clearly defined database interface, called DB-API 2.0. Furthermore, with a claimed installed base of SQLite
f more than >1 billion there is a lot of code out there and users are used to its programmatic interface. The goal was
set to follow the Python/SQLite3 interface as much as possible.

What is the solution to this problem?
=====================================
We followed a test-driven approach by starting with the test suite for Python/SQLite 3 and working our way through all
the cases covered. The old pymonetdb library gave us a quick start. Within a month we were able to cover over 80% of the
test cases. We ignored zz, because they were too SQLite specific. Summary of our experiences

How does it work?
=================
In this section we show a small example

Where is the database?
======================
One of the key factors in an embedded database system is the location of the persistent data, if it persists.  In
MonetDBe we opted for a simple interface based on URLs,
memory:, /OSpath/directory, file://filename?withoptions, monetdb://mapi_host:port/db?params. The benefit of this
approach is that one can start developing the application with :memory: storage and switch to the server version by
simply changing the connection point.

What to expect next?
====================

The first implementation of MonetDBe is limited to a single :memory: or /OSpath/directory case in combination with one
or more remote server based versions.

And how about debugging?
========================

Using an embedded database library also comes with mutual responsibility. Unlike a server solution, your program could
easily create lead to incorrect data being passed around or even peek/pook in the underlying database structures. A
logging scheme available in every MonetDBe core can be used to trace the behavior.

What are the caveats?
=====================

There are a few caveats to the approach presented. SQLite and MonetDBe do not align 100% on the same interpretation of
the SQL standard. MonetDBe is more strict. This may result in minor differences in error handling or even some surprises
in the results, because SQLite is less strict in its interpretation.

The MonetDBePython library is available from Pypi. You don’t need to install MonetDB itself. Several edges are currently
dealt with before MonetDBe becomes an official release, but users are more than welcome to try it out. Please drop us a
note on your experiences.
