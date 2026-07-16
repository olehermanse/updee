import sys
from pathlib import Path

from upd.find import find_upgrade_files


def main() -> int:
    files = find_upgrade_files(Path("."))
    if not files:
        print("No files to upgrade found")
        return 1
    for file in files:
        print(file)
    return 0


if __name__ == "__main__":
    sys.exit(main())
