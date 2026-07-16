# Backlog

Things we're planning on adding, in no particular order:

## Upgraders

- `package.json` / `package-lock.json` support, running the appropriate npm commands.
- More file types, for example `go.mod`, `Cargo.toml`, GitHub Actions workflows, and Dockerfile base images.

## CLI

- `--dry-run` flag to show what would be upgraded without changing anything.
- Accepting paths as arguments, to upgrade only some files / directories, or a repo other than the current directory.
- Summary output at the end: which files were upgraded, which were skipped, and which failed.

## Automation

- Git integration: create a branch and commit the upgrades.
- Opening pull requests with the changes, like dependabot / renovate.
- Running on a schedule against a list of repos.

## Project

- CI (GitHub Actions) running `make check` on pull requests.
- Publishing releases to PyPI.
- Publishing the docker image to a registry.
- Tag a first release (v0.1.0), so versions from setuptools-scm look reasonable.
