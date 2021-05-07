import logging
from re import compile, DOTALL

from monetdbe._lowlevel import ffi
from monetdbe._cffi.types_ import char_p

from monetdbe import exceptions

_logger = logging.getLogger(__name__)

error_matcher = compile(pattern=r"^(?P<exception_type>.*):(?P<namespace>.*):(?P<code>.*)!(?P<msg>.*)$", flags=DOTALL)

other_matchers = (
    ('07001', compile(pattern=r"^MALException:monetdbe.monetdbe_bind:(?P<msg>.*)", flags=DOTALL)),
    ('07001', compile(pattern=r"^MALException:monetdbe.monetdbe_execute:(?P<msg>.*)", flags=DOTALL)),
)

# MonetDB error codes
errors = {
    '2D000': exceptions.IntegrityError,  # COMMIT: failed
    '40000': exceptions.IntegrityError,  # DROP TABLE: FOREIGN KEY constraint violated
    '40002': exceptions.IntegrityError,  # INSERT INTO: UNIQUE constraint violated
    '42000': exceptions.OperationalError,  # SELECT: identifier 'asdf' unknown
    '42S02': exceptions.OperationalError,  # no such table
    '45000': exceptions.OperationalError,  # 'Result set construction failed'
    'M0M29': exceptions.IntegrityError,  # The code monetdb emitted before Jun2020
    '25001': exceptions.OperationalError,  # START TRANSACTION: cannot start a transaction within a transaction
    '07001': exceptions.ProgrammingError,  # Parameter .* not bound to a value
}


def check_error(raw: char_p) -> None:
    """
    Raises:
         exceptions.Error: or subclass in case of error, which exception depends on the error type.
    """
    if not raw:
        return

    decoded = ffi.string(raw).decode()
    _logger.error(decoded)
    match = error_matcher.match(decoded)

    if not match:
        for error_code, other_matcher in other_matchers:
            other_match = other_matcher.match(decoded)
            if other_match:
                exception = errors[error_code]
                msg = other_match.groups()[0]
                break
        else:
            # the error string is in an unknown format
            exception = exceptions.DatabaseError
            msg = decoded
    else:
        _, _, code, msg = match.groups()
        exception = errors.get(code, exceptions.DatabaseError)

    raise exception(msg)
