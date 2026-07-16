# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- `upd` CLI which finds dependency files (`package-lock.json`, `package.json`,
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
