import subprocess
from pathlib import Path

from updee.docker import upgrade_dockerfile
from updee.find import is_github_workflow
from updee.workflows import upgrade_workflow


class Skip:
    """A planner result meaning the file should not be upgraded."""

    def __init__(self, reason: str):
        self.reason = reason


def plan_pyproject(path: Path) -> list[list[str]] | Skip:
    try:
        content = path.read_text()
    except OSError:
        content = ""
    if "[tool.poetry]" in content or path.with_name("poetry.lock").exists():
        return Skip("managed by poetry, which is not supported yet")
    if path.with_name("uv.lock").exists():
        return Skip("uv.lock is upgraded instead")
    return [["uv", "lock", "--upgrade"]]


def plan_requirements_txt(path: Path) -> list[list[str]] | Skip:
    # If requirements.txt is compiled from a requirements.in, recompile from
    # that. Otherwise compile requirements.txt onto itself, which upgrades
    # anything not pinned with ==.
    source = path.with_name("requirements.in")
    if not source.exists():
        source = path
    return [["uv", "pip", "compile", source.name, "-o", path.name, "--upgrade"]]


def plan_uv_lock(path: Path) -> list[list[str]] | Skip:
    return [["uv", "lock", "--upgrade"]]


def plan_package_json(path: Path) -> list[list[str]] | Skip:
    # npm-check-updates bumps the version ranges in package.json itself,
    # npm install then updates package-lock.json and node_modules to match.
    # --yes stops npx from asking before downloading npm-check-updates:
    return [["npx", "--yes", "npm-check-updates", "-u"], ["npm", "install"]]


def plan_package_lock(path: Path) -> list[list[str]] | Skip:
    return [["npm", "update"]]


def plan_go_mod(path: Path) -> list[list[str]] | Skip:
    return [["go", "get", "-u", "./..."], ["go", "mod", "tidy"]]


def plan_cargo_toml(path: Path) -> list[list[str]] | Skip:
    if path.with_name("Cargo.lock").exists():
        return Skip("Cargo.lock is upgraded instead")
    return [["cargo", "update"]]


def plan_cargo_lock(path: Path) -> list[list[str]] | Skip:
    return [["cargo", "update"]]


PLANNERS = {
    "pyproject.toml": plan_pyproject,
    "requirements.txt": plan_requirements_txt,
    "uv.lock": plan_uv_lock,
    "package.json": plan_package_json,
    "package-lock.json": plan_package_lock,
    "go.mod": plan_go_mod,
    "Cargo.toml": plan_cargo_toml,
    "Cargo.lock": plan_cargo_lock,
}


def upgrade_file(path: Path, dry_run: bool = False, quiet: bool = False) -> str:
    """Upgrade path, returning a status for the summary:
    upgraded / skipped / failed / would upgrade"""
    if is_github_workflow(path):
        return upgrade_workflow(path, dry_run=dry_run, quiet=quiet)
    if path.name == "Dockerfile":
        return upgrade_dockerfile(path, dry_run=dry_run, quiet=quiet)
    planner = PLANNERS.get(path.name)
    if planner is None:
        if not quiet:
            print(f"{path}: skipping (upgrading this file type is not implemented yet)")
        return "skipped"
    plan = planner(path)
    if isinstance(plan, Skip):
        if not quiet:
            print(f"{path}: skipping ({plan.reason})")
        return "skipped"
    if dry_run:
        if not quiet:
            printable = "', then '".join(" ".join(command) for command in plan)
            print(f"{path}: would run '{printable}'")
        return "would upgrade"
    for command in plan:
        if not quiet:
            print(f"{path}: running '{' '.join(command)}'")
        output = subprocess.DEVNULL if quiet else None
        try:
            result = subprocess.run(
                command, cwd=path.parent, stdout=output, stderr=output
            )
        except FileNotFoundError:
            print(f"Error: '{command[0]}' not found - is it installed and in PATH?")
            return "failed"
        if result.returncode != 0:
            return "failed"
    return "upgraded"
