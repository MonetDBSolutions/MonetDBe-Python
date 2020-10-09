import logging
from re import compile, DOTALL

from monetdbe._lowlevel import ffi

from monetdbe import exceptions

_logger = logging.getLogger(__name__)
_error_match = compile(pattern=r"^(?P<exception_type>.*):(?P<namespace>.*):(?P<code>.*)!(?P<msg>.*)$", flags=DOTALL)

# MonetDB error codes
errors = {
    '2D000': exceptions.IntegrityError,  # COMMIT: failed
    '40000': exceptions.IntegrityError,  # DROP TABLE: FOREIGN KEY constraint violated
    '40002': exceptions.IntegrityError,  # INSERT INTO: UNIQUE constraint violated
    '42000': exceptions.OperationalError,  # SELECT: identifier 'asdf' unknown
    '42S02': exceptions.OperationalError,  # no such table
    'M0M29': exceptions.IntegrityError,  # The code monetdb emmitted before Jun2020
    '25001': exceptions.OperationalError,  # START TRANSACTION: cannot start a transaction within a transaction
}


def check_error(msg: 'ffi.CData') -> None:
    """
    Raises:
         exceptions.Error: or subclass in case of error, which exception depends on the error type.
    """
    if msg:
        decoded = ffi.string(msg).decode()
        _logger.error(decoded)
        match = _error_match.match(decoded)

        if not match:
            raise exceptions.OperationalError(decoded)

        _, _, error, msg = match.groups()

        if error not in errors:
            ...

        exception = errors.get(error, exceptions.DatabaseError)
        raise exception(msg)
