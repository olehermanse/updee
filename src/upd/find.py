import os
from pathlib import Path

UPGRADE_FILE_NAMES = (
    "package-lock.json",
    "package.json",
    "requirements.txt",
    "pyproject.toml",
)

SKIP_DIR_NAMES = (
    "node_modules",
    "venv",
    "build",
    "dist",
    "__pycache__",
)


def find_upgrade_files(root: Path) -> list[Path]:
    """Find files we know how to upgrade, recursively under root."""
    found = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [
            d for d in dirnames if not d.startswith(".") and d not in SKIP_DIR_NAMES
        ]
        for filename in filenames:
            if filename in UPGRADE_FILE_NAMES:
                found.append(Path(dirpath) / filename)
    return sorted(found)
