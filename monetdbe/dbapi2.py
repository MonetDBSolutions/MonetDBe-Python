# monetdbe/dbapi2.py: the DB-API 2.0 interface
#
# Copyright (C) 2004-2005 Gerhard Häring <gh@ghaering.de>
#
# This file is part of pymonetdbe.
#
# This software is provided 'as-is', without any express or implied
# warranty.  In no event will the authors be held liable for any damages
# arising from the use of this software.
#
# Permission is granted to anyone to use this software for any purpose,
# including commercial applications, and to alter it and redistribute it
# freely, subject to the following restrictions:
#
# 1. The origin of this software must not be misrepresented; you must not
#    claim that you wrote the original software. If you use this software
#    in a product, an acknowledgment in the product documentation would be
#    appreciated but is not required.
# 2. Altered source versions must be plainly marked as such, and must not be
#    misrepresented as being the original software.
# 3. This notice may not be removed or altered from any source distribution.
from datetime import date, time, datetime
from time import localtime

from monetdbe.connection import Connection

from monetdbe.cursor import Cursor
from monetdbe.exceptions import (
    IntegrityError, DatabaseError, StandardError, Error, DataError, InterfaceError, InternalError, NotSupportedError,
    OperationalError, ProgrammingError, Warning
)

OptimizedUnicode = str

paramstyle = "qmark"
threadsafety = 1
apilevel = "2.0"
Date = date
Time = time
Timestamp = datetime


def connect(*args, **kwargs):
    if 'factory' in kwargs:  # and 'database' in kwargs:
        factory = kwargs.pop('factory')
        return factory(*args, **kwargs)
        # return factory(database=kwargs['database'])
    return Connection(*args, **kwargs)


connect.__doc__ = Connection.__init__.__doc__


def DateFromTicks(ticks):
    return Date(*localtime(ticks)[:3])


def TimeFromTicks(ticks):
    return Time(*localtime(ticks)[3:6])


def TimestampFromTicks(ticks):
    return Timestamp(*localtime(ticks)[:6])


Binary = memoryview
