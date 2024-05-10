import zipfile


class ZipInfo(zipfile.ZipInfo):
    def __repr__(self) -> str:
        orig = super().__repr__()
        return orig + " - extrainfo wuz here"
