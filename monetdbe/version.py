import pkg_resources

try:
    __version__ = pkg_resources.require("monetdbe")[0].version  # type: str
except pkg_resources.DistributionNotFound:
    __version__ = "0.0"

version = __version__
monetdbe_version = __version__
version_info = tuple([int(x) for x in __version__.split(".")])
monetdbe_version_info = version_info
