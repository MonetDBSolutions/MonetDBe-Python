"""
This module contains all python code interacting with CFFI and should not be used directly from the outside world.
"""
import logging

_logger = logging.getLogger(__name__)


def check_if_we_can_import_lowlevel():
    try:
        from monetdbe._lowlevel import lib, ffi
    except ImportError as e:
        _logger.error(e)
        _logger.error("We recommend you use the MonetDBe-Python binary wheels.")
        _logger.error("If you can't or don't want to then:")
        _logger.error("On Linux: try setting LD_LIBRARY_PATH to point to the location of libmonetdbe.so.")
        _logger.error("On OS X: try setting DYLIB_LIBRARY_PATH to point to the location of libmonetdbe.so.")
        _logger.error("On Windows: try setting PATH to point to the location of libmonetdbe.dll.")
        _logger.error("Also make sure all depending shared libraries are available.")
        raise
