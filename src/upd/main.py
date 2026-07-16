import argparse
import sys
from pathlib import Path

from upd.find import find_upgrade_files
from upd.upgrade import upgrade_file
from upd.version import version_string


def _get_arg_parser():
    ap = argparse.ArgumentParser(
        prog="upd",
        description="Stupidly simple repo updater - "
        "finds dependency files in the current directory and upgrades them",
    )
    ap.add_argument(
        "--version",
        "-V",
        help="Print version number",
        action="version",
        version=version_string(),
    )
    return ap


def main(argv=None) -> int:
    _get_arg_parser().parse_args(argv)
    files = find_upgrade_files(Path("."))
    if not files:
        print("No files to upgrade found")
        return 1
    exit_code = 0
    for file in files:
        if upgrade_file(file) != 0:
            exit_code = 1
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
