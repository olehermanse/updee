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
        "finds dependency files and upgrades them",
    )
    ap.add_argument(
        "--version",
        "-V",
        help="Print version number",
        action="version",
        version=version_string(),
    )
    ap.add_argument(
        "--dry-run",
        help="Print the files that would be upgraded and the commands "
        "that would be run, without running them",
        action="store_true",
    )
    ap.add_argument(
        "paths",
        nargs="*",
        default=["."],
        help="Files / directories to look for upgrades in "
        "(default: current directory)",
    )
    return ap


def main(argv=None) -> int:
    args = _get_arg_parser().parse_args(argv)
    files = []
    for arg in args.paths:
        path = Path(arg)
        if path.is_dir():
            files.extend(find_upgrade_files(path))
        elif path.is_file():
            files.append(path)
        else:
            print(f"Error: '{arg}' is not a file or directory")
            return 1
    files = list(dict.fromkeys(files))
    if not files:
        print("No files to upgrade found")
        return 1
    exit_code = 0
    for file in files:
        if upgrade_file(file, dry_run=args.dry_run) != 0:
            exit_code = 1
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
