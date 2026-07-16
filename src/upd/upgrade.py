import subprocess
from pathlib import Path


def plan_pyproject(path: Path) -> list[str]:
    return ["uv", "lock", "--upgrade"]


def plan_requirements_txt(path: Path) -> list[str]:
    # If requirements.txt is compiled from a requirements.in, recompile from
    # that. Otherwise compile requirements.txt onto itself, which upgrades
    # anything not pinned with ==.
    source = path.with_name("requirements.in")
    if not source.exists():
        source = path
    return ["uv", "pip", "compile", source.name, "-o", path.name, "--upgrade"]


PLANNERS = {
    "pyproject.toml": plan_pyproject,
    "requirements.txt": plan_requirements_txt,
}


def upgrade_file(path: Path, dry_run: bool = False) -> int:
    planner = PLANNERS.get(path.name)
    if planner is None:
        print(f"{path}: skipping (upgrading this file type is not implemented yet)")
        return 0
    command = planner(path)
    if dry_run:
        print(f"{path}: would run '{' '.join(command)}'")
        return 0
    print(f"{path}: running '{' '.join(command)}'")
    try:
        result = subprocess.run(command, cwd=path.parent)
    except FileNotFoundError:
        print(f"Error: '{command[0]}' not found - is it installed and in PATH?")
        return 1
    return result.returncode
