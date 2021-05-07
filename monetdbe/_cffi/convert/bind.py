from typing import Any
import datetime
from monetdbe._lowlevel import ffi


def monetdbe_int(data: int):
    if data > 2 ** 32:
        return ffi.new("int64_t *", data)
    else:
        return ffi.new("int *", data)


def bind_str(data: str):
    return str(data).encode()


def bind_float(data: float):
    return ffi.new("float *", data)


def bind_bytes(data: bytes):
    return f"{data.hex()}".encode()


def bind_memoryview(data: memoryview):
    return f"{data.tobytes().hex()}".encode()


def bind_datetime(data: datetime.datetime):
    struct = ffi.new("monetdbe_data_timestamp *")
    struct.date.day = data.day
    struct.date.month = data.month
    struct.date.year = data.year
    struct.time.ms = int(data.microsecond / 1000)
    struct.time.seconds = data.second
    struct.time.minutes = data.minute
    struct.time.hours = data.hour
    return struct


def bind_time(data: datetime.time):
    struct = ffi.new("monetdbe_data_time *")
    struct.ms = int(data.microsecond / 1000)
    struct.seconds = data.second
    struct.minutes = data.minute
    struct.hours = data.hour
    return struct


def bind_date(data: datetime.date):
    struct = ffi.new("monetdbe_data_date *")
    struct.day = data.day
    struct.month = data.month
    struct.year = data.year
    return struct


def bind_timedelta(data: datetime.timedelta):
    struct = ffi.new("monetdbe_data_time *")
    struct.ms = int(data.microseconds / 1000)
    struct.seconds = data.seconds
    struct.minutes = 0
    struct.hours = 0
    return struct


map_ = {
    int: monetdbe_int,
    datetime.datetime: bind_datetime,
    datetime.time: bind_time,
    datetime.date: bind_date,
    datetime.timedelta: bind_timedelta,
    str: bind_str,
    float: bind_float,
    bytes: bind_bytes,
    memoryview: bind_memoryview,
}


def prepare_bind(data: Any):
    try:
        return map_[type(data)](data)
    except KeyError:
        for type_, func in map_.items():
            if isinstance(data, type_):
                return func(data)
        raise NotImplementedError(f"bind converting for type {type(data)}")
