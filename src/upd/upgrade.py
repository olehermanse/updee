import subprocess
from pathlib import Path


def _run(command: list[str], cwd: Path) -> int:
    print(f"{cwd}: running '{' '.join(command)}'")
    try:
        result = subprocess.run(command, cwd=cwd)
    except FileNotFoundError:
        print(f"Error: '{command[0]}' not found - is it installed and in PATH?")
        return 1
    return result.returncode


def upgrade_pyproject(path: Path) -> int:
    return _run(["uv", "lock", "--upgrade"], cwd=path.parent)


def upgrade_requirements_txt(path: Path) -> int:
    # If requirements.txt is compiled from a requirements.in, recompile from
    # that. Otherwise compile requirements.txt onto itself, which upgrades
    # anything not pinned with ==.
    source = path.with_name("requirements.in")
    if not source.exists():
        source = path
    return _run(
        ["uv", "pip", "compile", source.name, "-o", path.name, "--upgrade"],
        cwd=path.parent,
    )


UPGRADERS = {
    "pyproject.toml": upgrade_pyproject,
    "requirements.txt": upgrade_requirements_txt,
}


def upgrade_file(path: Path) -> int:
    upgrader = UPGRADERS.get(path.name)
    if upgrader is None:
        print(f"{path}: skipping (upgrading this file type is not implemented yet)")
        return 0
    return upgrader(path)
