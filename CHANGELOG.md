# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Upgrading of GitHub Actions workflows (`.github/workflows/*.yml`), replacing
  version tags like `actions/checkout@v4` with the latest release tag from the
  GitHub API. The pinned precision is kept (`v4` becomes `v5`, `v4.1.0` becomes
  `v5.0.2`), and SHA / branch pins are left alone. Requests are authenticated
  with the `GITHUB_TOKEN` environment variable, if set.
- Upgrading of `package-lock.json`, by running `npm update`.
- Upgrading of `package.json`, by running `npx npm-check-updates -u` followed
  by `npm install`, to also bump the version ranges in the file.
- Upgrading of `go.mod`, by running `go get -u ./...` followed by
  `go mod tidy`.
- Upgrading of `Cargo.toml` / `Cargo.lock`, by running `cargo update`
  (`Cargo.toml` defers to `Cargo.lock` when both are present).
- Upgrading of `uv.lock`, by running `uv lock --upgrade`. `pyproject.toml`
  defers to `uv.lock` when both are present, and poetry-managed projects are
  skipped with a clear message.
- Upgrading of `Dockerfile` base images, replacing version tags in `FROM`
  lines (e.g. `python:3.13-slim` becomes `python:3.14-slim`) with the latest
  tag of the same shape from Docker Hub. Images outside Docker Hub, `latest`
  tags, and digest pins are left alone.
- npm, go, and cargo in the docker image, for the new upgraders.

### Fixed

- The docker image failed to build since the rename to updee, because the
  Dockerfile still set the `SETUPTOOLS_SCM_PRETEND_VERSION_FOR_UPD` (not
  `..._FOR_UPDEE`) environment variable.

## [0.0.1] - 2026-07-16

### Added

- `updee` CLI which finds dependency files (`package-lock.json`, `package.json`,
  `requirements.txt`, `pyproject.toml`) in the current directory and upgrades
  the ones it has support for.
- Upgrading of `pyproject.toml` projects, by running `uv lock --upgrade`.
- Upgrading of `requirements.txt` files, by running `uv pip compile --upgrade`,
  recompiling from `requirements.in` if present.
- `--version` / `-V` and `--help` / `-h` flags.
- Dockerfile for running upd in a repo / folder mounted at `/repo`, with all
  the CLIs upd relies on preinstalled.
- `--dry-run` flag, printing the files that would be upgraded and the commands
  that would be run, without running them.
- Positional `paths` arguments, to upgrade only the given files / directories,
  defaulting to the current directory.
- `--only` flag, to filter which file names to upgrade,
  e.g. `--only pyproject.toml,requirements.txt`.
- Summary table at the end of each run, with one line per file:
  upgraded / skipped / failed / would upgrade.
- `--quiet` / `-q` flag, to only print the summary, hiding progress and
  subcommand output.
- GitHub Actions workflow running `make check` on pushes and pull requests,
  on Linux and macOS, python 3.10 - 3.14.
- GitHub Actions workflow publishing releases to PyPI
  (when a GitHub release is published).
