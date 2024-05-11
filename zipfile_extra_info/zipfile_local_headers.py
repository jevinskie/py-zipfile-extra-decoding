import enum
import os
import zipfile
from typing import IO, Any, Literal, cast, overload

# TODO: use TypeAlias for these two when mypy bugs are fixed
# https://github.com/python/mypy/issues/16581
_ZipFileMode = Literal["r", "w", "x", "a"]  # noqa: Y026


class CompressionMethod(enum.IntEnum):
    ZIP_STORED = 0
    ZIP_DEFLATED = 8
    ZIP_BZIP2 = 12
    ZIP_LZMA = 14


class ZipFileLocalHeaders(zipfile.ZipFile):
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


zipfile.ZipFile = ZipFileLocalHeaders  # type: ignore
