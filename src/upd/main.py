import argparse
import sys
from pathlib import Path

from upd.find import UPGRADE_FILE_NAMES, find_upgrade_files
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
        "--only",
        help="Comma-separated list of file names to upgrade, "
        "e.g. 'pyproject.toml,requirements.txt' (default: all supported files)",
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
    only = None
    if args.only:
        only = args.only.split(",")
        unknown = [name for name in only if name not in UPGRADE_FILE_NAMES]
        if unknown:
            print(f"Error: unknown file name(s): {', '.join(unknown)}")
            print(f"Supported file names: {', '.join(UPGRADE_FILE_NAMES)}")
            return 1
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
    if only is not None:
        files = [f for f in files if f.name in only]
    if not files:
        print("No files to upgrade found")
        return 1
    results = []
    for file in files:
        results.append((file, upgrade_file(file, dry_run=args.dry_run)))
    width = max(len(str(file)) for file, _ in results)
    print("Summary:")
    for file, status in results:
        print(f"  {str(file):<{width}}  {status}")
    if any(status == "failed" for _, status in results):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
