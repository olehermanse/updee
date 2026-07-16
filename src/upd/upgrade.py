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


def upgrade_file(path: Path, dry_run: bool = False, quiet: bool = False) -> str:
    """Upgrade path, returning a status for the summary:
    upgraded / skipped / failed / would upgrade"""
    planner = PLANNERS.get(path.name)
    if planner is None:
        if not quiet:
            print(f"{path}: skipping (upgrading this file type is not implemented yet)")
        return "skipped"
    command = planner(path)
    if dry_run:
        if not quiet:
            print(f"{path}: would run '{' '.join(command)}'")
        return "would upgrade"
    if not quiet:
        print(f"{path}: running '{' '.join(command)}'")
    output = subprocess.DEVNULL if quiet else None
    try:
        result = subprocess.run(command, cwd=path.parent, stdout=output, stderr=output)
    except FileNotFoundError:
        print(f"Error: '{command[0]}' not found - is it installed and in PATH?")
        return "failed"
    if result.returncode != 0:
        return "failed"
    return "upgraded"
