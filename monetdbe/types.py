"""
definition of MonetDB column types, for more info:
http://www.monetdb.org/Documentation/Manuals/SQLreference/Datatypes
"""
import datetime
import time

CHAR = 'char'  # (L) character string with length L
VARCHAR = 'varchar'  # (L) string with atmost length L
CLOB = 'clob'  # string with no limit on size
BLOB = 'blob'  # binary data

TINYINT = 'tinyint'  # 8 bit integer
SMALLINT = 'smallint'  # 16 bit integer
INT = 'int'  # 32 bit integer
BIGINT = 'bigint'  # 64 bit integer
HUGEINT = 'hugeint'  # 128 bit integer
SERIAL = 'serial'  # special 64 bit integer sequence generator
REAL = 'real'  # 32 bit floating point
DOUBLE = 'double'  # 64 bit floating point
DECIMAL = 'decimal'  # (P,S)
BOOLEAN = 'boolean'  # boolean value

DATE = 'date'  # (D) date
TIME = 'time'  # (T) time of day
TIMESTAMP = 'timestamp'  # (T) date concatenated with unique time
MONTH_INTERVAL = 'month_interval'  # number of months
SEC_INTERVAL = 'sec_interval'  # number of seconds

URL = 'url'  # url
INET = 'inet'  # ipv4 address
UUID = 'uuid'  # uuid
JSON = 'json'  # JSON string
GEOMETRY = 'geometry'  # geometry string
GEOMETRYA = 'geometrya'  # geometry string

# Not on the website:
SHORTINT = 'shortint'
MEDIUMINT = 'mediumint'
LONGINT = 'longint'
OID = 'oid'
WRD = 'wrd'
FLOAT = 'float'  # 64 bit floating point
TIMESTAMPTZ = 'timestamptz'  # with timezone
TIMETZ = 'timetz'  # with timezone
INTERVAL = 'interval'  # (Q) a temporal interval

# full names and aliases, spaces are replaced with underscores
CHARACTER = CHAR
CHARACTER_VARYING = VARCHAR
CHARACHTER_LARGE_OBJECT = CLOB
BINARY_LARGE_OBJECT = BLOB
NUMERIC = DECIMAL
DOUBLE_PRECISION = DOUBLE

