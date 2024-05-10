import zipfile as _zipfile
from zipfile import (
    ZIP_BZIP2,
    ZIP_DEFLATED,
    ZIP_LZMA,
    ZIP_STORED,
    BadZipFile,
    BadZipfile,
    LargeZipFile,
    Path,
    PyZipFile,
    ZipFile,
    error,
    is_zipfile,
)

from . import tools, zipinfo
from ._version import __version__ as __version__

# _zipfile.ZipInfo = cast(zipinfo.ZipInfo, _zipfile.ZipInfo)
_zipfile.ZipInfo = zipinfo.ZipInfo  # type: ignore

__all__ = [
    "BadZipFile",
    "BadZipfile",
    "LargeZipFile",
    "Path",
    "PyZipFile",
    "ZIP_BZIP2",
    "ZIP_DEFLATED",
    "ZIP_LZMA",
    "ZIP_STORED",
    "ZipFile",
    "ZipInfo",
    "error",
    "is_zipfile",
    "tools",
]
