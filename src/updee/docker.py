import json
import re
import urllib.error
import urllib.request
from pathlib import Path

# Lines like 'FROM python:3.13-slim AS builder':
FROM_LINE = re.compile(
    r"^(?P<prefix>\s*FROM\s+(?:--platform=\S+\s+)?)"
    r"(?P<image>[a-z0-9][a-z0-9._/-]*)"
    r":(?P<tag>[A-Za-z0-9._-]+)"
    r"(?P<rest>(?:\s.*)?)$",
    re.IGNORECASE,
)

# Only tags which look like versions are upgraded, split into the numeric
# part and a variant suffix ('3.13-slim' -> '3.13' and '-slim'):
VERSION_TAG = re.compile(r"^(?P<version>v?\d+(?:\.\d+)*)(?P<suffix>-[A-Za-z0-9._-]+)?$")

# Docker Hub returns tags newest-first, so the latest version of an actively
# maintained image is in the first pages - don't fetch thousands of old tags:
PAGE_LIMIT = 10


def _hub_repository(image: str) -> str | None:
    """The Docker Hub repository for an image, or None if it is not on
    Docker Hub ('python' -> 'library/python', 'ghcr.io/foo/bar' -> None)."""
    if "/" not in image:
        return f"library/{image}"
    first = image.split("/")[0]
    if "." in first or ":" in first or image.count("/") > 1:
        return None
    return image


def image_tags(image: str) -> list[str] | None:
    """Tags of an image on Docker Hub, newest first, or None if the image
    is not on Docker Hub."""
    repository = _hub_repository(image)
    if repository is None:
        return None
    url = f"https://hub.docker.com/v2/repositories/{repository}/tags?page_size=100"
    headers = {"Accept": "application/json", "User-Agent": "updee"}
    tags = []
    for _ in range(PAGE_LIMIT):
        request = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                data = json.load(response)
        except urllib.error.HTTPError as error:
            if error.code == 404:
                return None
            raise
        tags.extend(result["name"] for result in data.get("results", []))
        url = data.get("next")
        if not url:
            break
    return tags


def _version_tuple(version: str) -> tuple[int, ...]:
    return tuple(int(part) for part in version.removeprefix("v").split("."))


def latest_tag(current: str, tags: list[str]) -> str | None:
    """The newest of tags with the same shape as current: same 'v' prefix,
    precision and suffix ('3.11-slim' only considers 'X.Y-slim' tags).
    None if there is nothing newer."""
    match = VERSION_TAG.match(current)
    if match is None:
        return None
    version, suffix = match["version"], match["suffix"] or ""
    best = _version_tuple(version)
    best_tag = None
    for tag in set(tags):
        candidate = VERSION_TAG.match(tag)
        if candidate is None:
            continue
        if (candidate["suffix"] or "") != suffix:
            continue
        candidate_version = candidate["version"]
        if candidate_version.startswith("v") != version.startswith("v"):
            continue
        if len(candidate_version.split(".")) != len(version.split(".")):
            continue
        numbers = _version_tuple(candidate_version)
        if numbers > best:
            best = numbers
            best_tag = tag
    return best_tag


def update_base_images(content: str) -> tuple[str, list[str]]:
    """Replace version tags in FROM lines with the latest Docker Hub tags.

    Returns the new content and a list of changes for printing."""
    cache: dict[str, list[str] | None] = {}
    changes = []
    lines = content.splitlines(keepends=True)
    for i, line in enumerate(lines):
        stripped = line.rstrip("\r\n")
        match = FROM_LINE.match(stripped)
        if match is None:
            continue
        tag = match["tag"]
        if not VERSION_TAG.match(tag):
            continue
        image = match["image"]
        if image not in cache:
            cache[image] = image_tags(image)
        tags = cache[image]
        if tags is None:
            continue
        new_tag = latest_tag(tag, tags)
        if new_tag is None:
            continue
        ending = line[len(stripped) :]
        lines[i] = f"{match['prefix']}{image}:{new_tag}{match['rest']}{ending}"
        changes.append(f"{image} {tag} -> {new_tag}")
    return "".join(lines), changes


def upgrade_dockerfile(path: Path, dry_run: bool = False, quiet: bool = False) -> str:
    """Upgrade the base images in a Dockerfile, returning a status for the
    summary: upgraded / failed / would upgrade"""
    if dry_run:
        if not quiet:
            print(f"{path}: would update base images to their latest versions")
        return "would upgrade"
    if not quiet:
        print(f"{path}: updating base images to their latest versions")
    try:
        content, changes = update_base_images(path.read_text())
    except (urllib.error.URLError, TimeoutError) as error:
        reason = getattr(error, "reason", error)
        print(f"Error: Docker Hub API request failed ({reason})")
        return "failed"
    if changes:
        path.write_text(content)
    if not quiet:
        for change in changes:
            print(f"{path}: {change}")
        if not changes:
            print(f"{path}: all base images already up to date")
    return "upgraded"
