import enum
import os
import struct
import zipfile
from typing import IO, Any, Literal, TypeVar, cast, overload

from . import BadZipFile
from .zipinfo_extra_info import ZipInfoExtInfo

# TODO: use TypeAlias for these two when mypy bugs are fixed
# https://github.com/python/mypy/issues/16581
_ZipFileMode = Literal["r", "w", "x", "a"]  # noqa: Y026

_T = TypeVar("_T")


class CompressionMethod(enum.IntEnum):
    ZIP_STORED = 0
    ZIP_DEFLATED = 8
    ZIP_BZIP2 = 12
    ZIP_LZMA = 14


def _get_zipfile_private(name: str, ty: type[_T]) -> _T:
    res = getattr(zipfile, name, None)
    if res is None:
        raise ValueError(f"Couldn't get zipfile.{name}")
    if not isinstance(res, ty):
        raise TypeError(
            f"zipfile.{name} is of type {type(res).__name__} but was expecting {ty.__name__}"
        )
    return res


_MASK_COMPRESSED_PATCH: int = _get_zipfile_private("_MASK_COMPRESSED_PATCH", int)
_MASK_STRONG_ENCRYPTION: int = _get_zipfile_private("_MASK_STRONG_ENCRYPTION", int)
_MASK_UTF_FILENAME: int = _get_zipfile_private("_MASK_UTF_FILENAME", int)

_FH_SIGNATURE: int = _get_zipfile_private("_FH_SIGNATURE", int)
_FH_EXTRACT_VERSION: int = _get_zipfile_private("_FH_EXTRACT_VERSION", int)
_FH_EXTRACT_SYSTEM: int = _get_zipfile_private("_FH_EXTRACT_SYSTEM", int)
_FH_GENERAL_PURPOSE_FLAG_BITS: int = _get_zipfile_private("_FH_GENERAL_PURPOSE_FLAG_BITS", int)
_FH_COMPRESSION_METHOD: int = _get_zipfile_private("_FH_COMPRESSION_METHOD", int)
_FH_LAST_MOD_TIME: int = _get_zipfile_private("_FH_LAST_MOD_TIME", int)
_FH_LAST_MOD_DATE: int = _get_zipfile_private("_FH_LAST_MOD_DATE", int)
_FH_CRC: int = _get_zipfile_private("_FH_CRC", int)
_FH_COMPRESSED_SIZE: int = _get_zipfile_private("_FH_COMPRESSED_SIZE", int)
_FH_UNCOMPRESSED_SIZE: int = _get_zipfile_private("_FH_UNCOMPRESSED_SIZE", int)
_FH_FILENAME_LENGTH: int = _get_zipfile_private("_FH_FILENAME_LENGTH", int)
_FH_EXTRA_FIELD_LENGTH: int = _get_zipfile_private("_FH_EXTRA_FIELD_LENGTH", int)

_structFileHeader: str = _get_zipfile_private("structFileHeader", str)
_stringFileHeader: bytes = _get_zipfile_private("stringFileHeader", bytes)
_sizeFileHeader: int = _get_zipfile_private("sizeFileHeader", int)

_SharedFile: type = _get_zipfile_private("_SharedFile", type(type))


class ZipFileLocalHeaders(zipfile.ZipFile):
    __slots__ = ("filelist_local",)
    filelist_local: list[ZipInfoExtInfo]

    @overload
    def __init__(
        self,
        file: str | os.PathLike[str] | IO[bytes],
        mode: Literal["r"] = "r",
        compression: int = 0,
        allowZip64: bool = True,
        compresslevel: int | None = None,
        *,
        strict_timestamps: bool = True,
        metadata_encoding: str | None,
    ) -> None: ...
    @overload
    def __init__(
        self,
        file: str | os.PathLike[str] | IO[bytes],
        mode: _ZipFileMode = "r",
        compression: int = 0,
        allowZip64: bool = True,
        compresslevel: int | None = None,
        *,
        strict_timestamps: bool = True,
        metadata_encoding: None = None,
    ) -> None: ...

    def __init__(
        self,
        file: str | os.PathLike[str] | IO[bytes],
        mode: _ZipFileMode = "r",
        compression: int = CompressionMethod.ZIP_STORED,
        allowZip64: bool = True,
        compresslevel: int | None = None,
        *,
        strict_timestamps: bool = True,
        metadata_encoding: str | None = None,
    ) -> None:
        super().__init__(
            file,
            cast(Any, mode),
            compression=compression,
            allowZip64=allowZip64,
            compresslevel=compresslevel,
            strict_timestamps=strict_timestamps,
            metadata_encoding=metadata_encoding,
        )
        self.filelist_local = []
        for cinfo in self.filelist:
            self.filelist_local.append(
                self.get_local_ZipInfo(name=cinfo.filename, metadata_encoding=metadata_encoding)
            )
            pass

    def get_local_ZipInfo(self, name: str, metadata_encoding: str | None = None) -> ZipInfoExtInfo:
        if not self.fp:
            raise ValueError("Attempt to use ZIP archive that was already closed")

        czinfo = self.getinfo(name)
        lzinfo = ZipInfoExtInfo(name, czinfo.date_time)

        # Open for reading:
        self._fileRefCnt += 1  # type: ignore
        zef_file = _SharedFile(
            self.fp,
            czinfo.header_offset,
            getattr(self, "_fpclose"),
            getattr(self, "_lock"),
            lambda: getattr(self, "_writing"),
        )
        try:
            # Skip the file header:
            fheader = zef_file.read(_sizeFileHeader)
            if len(fheader) != _sizeFileHeader:
                raise BadZipFile("Truncated file header")
            fheader = struct.unpack(_structFileHeader, fheader)
            if fheader[_FH_SIGNATURE] != _stringFileHeader:
                raise BadZipFile("Bad magic number for file header")

            fname: bytes = zef_file.read(fheader[_FH_FILENAME_LENGTH])
            if fheader[_FH_GENERAL_PURPOSE_FLAG_BITS] & _MASK_UTF_FILENAME:
                # UTF-8 filename
                fname_str = fname.decode("utf-8")
            else:
                fname_str = fname.decode(metadata_encoding or "cp437")
            lzinfo.orig_filename = fname_str
            if fname_str != lzinfo.orig_filename:
                raise BadZipFile(
                    f"File name in directory {lzinfo.orig_filename!r} and header {fname!r} differ."
                )
            filename = fname_str
            null_byte = filename.find(chr(0))
            if null_byte >= 0:
                filename = filename[0:null_byte]
            lzinfo.filename = filename
            if fheader[_FH_EXTRA_FIELD_LENGTH]:
                lzinfo.extra = zef_file.read(fheader[_FH_EXTRA_FIELD_LENGTH])

            if czinfo.flag_bits & _MASK_COMPRESSED_PATCH:
                # Zip 2.7: compressed patched data
                raise NotImplementedError("compressed patched data (flag bit 5)")

            if czinfo.flag_bits & _MASK_STRONG_ENCRYPTION:
                # strong encryption
                raise NotImplementedError("strong encryption (flag bit 6)")
            lzinfo._decodeExtra()
            zef_file.close()
            return lzinfo
        except Exception:
            zef_file.close()
            raise

    def infolist_local(self) -> list[ZipInfoExtInfo]:
        """Return a list of class ZipInfo instances for files in the
        archive based off of their local file headers."""
        return self.filelist_local


zipfile.ZipFile = ZipFileLocalHeaders  # type: ignore
