import json
import os
import re
import urllib.error
import urllib.request
from pathlib import Path

# Lines like '      - uses: actions/checkout@v4  # comment':
USES_LINE = re.compile(
    r"^(?P<prefix>\s*(?:-\s+)?uses:\s*)"
    r"(?P<action>[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+(?:/[^\s@]+)?)"
    r"@(?P<ref>[^\s#]+)"
    r"(?P<rest>.*)$"
)

# Only refs which look like version tags are upgraded, not SHAs / branches:
VERSION_REF = re.compile(r"^v?\d+(\.\d+){0,2}$")


def latest_version(repo: str) -> str | None:
    """Latest release tag of github.com/<repo>, or None if it has no releases."""
    url = f"https://api.github.com/repos/{repo}/releases/latest"
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "updee"}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.load(response).get("tag_name")
    except urllib.error.HTTPError as error:
        if error.code == 404:
            return None
        raise


def _same_precision(latest: str, current: str) -> str:
    """Truncate latest ('v5.0.2') to the precision of current ('v4' -> 'v5')."""
    prefix = "v" if latest.startswith("v") else ""
    parts = latest.removeprefix("v").split(".")
    wanted = len(current.removeprefix("v").split("."))
    return prefix + ".".join(parts[:wanted])


def update_actions(content: str) -> tuple[str, list[str]]:
    """Replace version refs in uses: lines with the latest release tags.

    Returns the new content and a list of changes for printing."""
    cache: dict[str, str | None] = {}
    changes = []
    lines = content.splitlines(keepends=True)
    for i, line in enumerate(lines):
        stripped = line.rstrip("\r\n")
        match = USES_LINE.match(stripped)
        if match is None:
            continue
        ref = match["ref"]
        if not VERSION_REF.match(ref):
            continue
        action = match["action"]
        repo = "/".join(action.split("/")[:2])
        if repo not in cache:
            cache[repo] = latest_version(repo)
        latest = cache[repo]
        if latest is None or not VERSION_REF.match(latest):
            continue
        new_ref = _same_precision(latest, ref)
        if new_ref == ref:
            continue
        ending = line[len(stripped) :]
        lines[i] = f"{match['prefix']}{action}@{new_ref}{match['rest']}{ending}"
        changes.append(f"{action} {ref} -> {new_ref}")
    return "".join(lines), changes


def upgrade_workflow(path: Path, dry_run: bool = False, quiet: bool = False) -> str:
    """Upgrade the actions in a workflow file, returning a status for the
    summary: upgraded / failed / would upgrade"""
    if dry_run:
        if not quiet:
            print(f"{path}: would update GitHub Actions to their latest versions")
        return "would upgrade"
    if not quiet:
        print(f"{path}: updating GitHub Actions to their latest versions")
    try:
        content, changes = update_actions(path.read_text())
    except (urllib.error.URLError, TimeoutError) as error:
        reason = getattr(error, "reason", error)
        print(f"Error: GitHub API request failed ({reason})")
        return "failed"
    if changes:
        path.write_text(content)
    if not quiet:
        for change in changes:
            print(f"{path}: {change}")
        if not changes:
            print(f"{path}: all actions already up to date")
    return "upgraded"
