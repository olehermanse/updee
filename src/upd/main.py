import sys
from pathlib import Path

from upd.find import find_upgrade_files
from upd.upgrade import upgrade_file


def main() -> int:
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
