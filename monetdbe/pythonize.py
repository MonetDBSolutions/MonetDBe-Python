from datetime import datetime, date, time
import re

Binary = bytes


def strip(data):
    """ returns a python string, with chopped off quotes,
    and replaced escape characters"""
    return ''.join([w.encode('utf-8').decode('unicode_escape')
                    if '\\' in w else w
                    for w in re.split('([\000-\200]+)', data[1:-1])])


def py_bool(data):
    """ return python boolean """
    return data == "true"


def py_time(data):
    """ returns a python Time
    """
    return time(hour=data.hours, minute=data.minutes, second=data.seconds, microsecond=data.ms * 1000)


def py_date(data):
    """ Returns a python Date
    """
    return date(year=data.year, month=data.month, day=data.day)


def py_timestamp(data):
    """ Returns a python Timestamp
    """
    return datetime(year=data.date.year,
                    month=data.date.month,
                    day=data.date.day,
                    hour=data.time.hours,
                    minute=data.time.minutes,
                    second=data.time.seconds,
                    microsecond=data.time.ms * 1000)


def py_bytes(data):
    """Returns a bytes object representing the input blob."""
    return Binary(data)


def oid(data):
    """represents an object identifier
    For now we will just return the string representation just like mclient does.
    """
    return oid
