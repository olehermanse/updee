import os
from pathlib import Path

UPGRADE_FILE_NAMES = (
    "package-lock.json",
    "package.json",
    "requirements.txt",
    "pyproject.toml",
    "uv.lock",
    "go.mod",
    "Cargo.toml",
    "Cargo.lock",
    "Dockerfile",
)

SKIP_DIR_NAMES = (
    "node_modules",
    "venv",
    "build",
    "dist",
    "__pycache__",
)


def is_github_workflow(path: Path) -> bool:
    """Whether path is a GitHub Actions workflow (.github/workflows/*.yml)."""
    return (
        path.suffix in (".yml", ".yaml")
        and path.parent.name == "workflows"
        and path.parent.parent.name == ".github"
    )


def find_upgrade_files(root: Path) -> list[Path]:
    """Find files we know how to upgrade, recursively under root."""
    found = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [
            d
            for d in dirnames
            if (not d.startswith(".") or d == ".github") and d not in SKIP_DIR_NAMES
        ]
        for filename in filenames:
            path = Path(dirpath) / filename
            if filename in UPGRADE_FILE_NAMES or is_github_workflow(path):
                found.append(path)
    return sorted(found)
