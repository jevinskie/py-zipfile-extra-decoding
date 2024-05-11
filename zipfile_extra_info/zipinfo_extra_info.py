import struct
import sys
import zipfile

import whenever as whenever

from . import BadZipFile


class ZipInfoExtInfo(zipfile.ZipInfo):
    __slots__ = ("date_time_norm", "ext_atime", "ext_ctime", "ext_mtime")
    date_time_norm: whenever.UTCDateTime
    ext_atime: whenever.UTCDateTime | None
    ext_ctime: whenever.UTCDateTime | None
    ext_mtime: whenever.UTCDateTime | None

    def __init__(
        self,
        filename: str = "NoName",
        date_time: tuple[int, int, int, int, int, int] = (1980, 1, 1, 0, 0, 0),
    ):
        super().__init__(filename=filename, date_time=date_time)
        self.date_time_norm = whenever.UTCDateTime(*self.date_time)
        self.ext_atime = None
        self.ext_ctime = None
        self.ext_mtime = None

    def _decodeExtendedTime(self) -> None:
        extra = self.extra
        unpack = struct.unpack
        while len(extra) >= 4:
            tp, ln = unpack("<HH", extra[:4])
            if ln + 4 > len(extra):
                raise BadZipFile(f"Corrupt extra field {tp:04x} (size={ln})")
            if tp == 0x5455:
                data = extra[4 : ln + 4]
                try:
                    i = 0
                    flags = data[i]
                    i += 1
                    mtime_present = bool(flags & (1 << 0))
                    atime_present = bool(flags & (1 << 1))
                    ctime_present = bool(flags & (1 << 2))
                    if mtime_present and atime_present and len(data) == 5:
                        try:
                            f = sys._getframe()
                            assert f.f_back is not None
                            f = f.f_back
                            assert f.f_back is not None
                            f = f.f_back
                            assert f.f_code is not None
                            if f.f_code.co_name != "_RealGetContents":
                                raise BadZipFile(
                                    "Corrupt extended time ('UT') extra field. mtime and atime are indicated as present but length is 5 and it is not a Central Directory entry where this exception is the norm"
                                ) from None
                        except Exception as e:
                            raise BadZipFile(
                                f"Exception encountered when trying to backtrace to determine if ZipInfo creation is for a Central Directory entry when trying to determine if extended time ('UT') extra field where mtime and atime are indicated present but data length is only 5. Exception: {e}"
                            ) from None
                        atime_present = False
                    if mtime_present:
                        self.ext_mtime = whenever.UTCDateTime.from_timestamp(
                            unpack("<I", data[i : i + 4])[0]
                        )
                        i += 4
                    if atime_present:
                        self.ext_atime = whenever.UTCDateTime.from_timestamp(
                            unpack("<I", data[i : i + 4])[0]
                        )
                        i += 4
                    if ctime_present:
                        self.ext_atime = whenever.UTCDateTime.from_timestamp(
                            unpack("<I", data[i : i + 4])[0]
                        )
                        i += 4
                except struct.error as e:
                    raise BadZipFile(
                        f"Corrupt extended time ('UT') extra field. struct exception: {e}"
                    ) from None
            extra = extra[ln + 4 :]

    def _decodeExtra(self) -> None:
        super()._decodeExtra()  # type: ignore
        self._decodeExtendedTime()


zipfile.ZipInfo = ZipInfoExtInfo  # type: ignore
