#!/usr/bin/env python3

import argparse
import logging
import sys
from pathlib import Path

from packaging.version import Version
from rich import print
from rich.console import Console
from rich.logging import RichHandler

from zipfile_extra_info import ZipFile, _version

LOG_FORMAT = "%(message)s"
logging.basicConfig(
    level=logging.WARNING,
    format=LOG_FORMAT,
    datefmt="[%X]",
    handlers=[RichHandler(console=Console(stderr=True), rich_tracebacks=True)],
)

program_name = "zipfile-extra-info"

log = logging.getLogger(program_name)


def get_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog=program_name)
    parser.add_argument("zip_file", metavar="<ZIP FILE>", type=Path, help="Input zip file.")
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s version: {Version(_version.version)}",
    )
    return parser


def real_main(args: argparse.Namespace) -> int:
    with ZipFile(args.zip_file) as f:
        for i in f.infolist():
            print(i)
    return 0


def main() -> int:
    try:
        return real_main(get_arg_parser().parse_args())
    except Exception:
        log.exception(f"Received an unexpected exception when running {program_name}")
        return 1
    except KeyboardInterrupt:
        return 0


if __name__ == "__main__":
    sys.exit(main())
