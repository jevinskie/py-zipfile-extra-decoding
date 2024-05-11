# import zipfile as _zipfile


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

from ._version import __version__ as __version__
from .zipinfo_extra_info import ZipInfoExtInfo as ZipInfo

from . import tools  # isort: skip

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
