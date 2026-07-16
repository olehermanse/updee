# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
