# Backlog

Things we're planning on adding, in no particular order:

## Upgraders

- `package-lock.json`: run `npm update`.
- `package.json`: run `npx npm-check-updates -u` followed by `npm install`, to also bump the version ranges in the file.
- `go.mod`: run `go get -u ./...` followed by `go mod tidy`.
- `Cargo.toml` / `Cargo.lock`: run `cargo update`.
- `uv.lock` in repos where we find it without pyproject.toml changes needed (currently we key on `pyproject.toml`; a `pyproject.toml` without uv, e.g. poetry, should be detected and skipped with a clear message).
- GitHub Actions workflows (`.github/workflows/*.yml`): bump `uses:` action versions to the latest tag.
- `Dockerfile`: bump the image tags in `FROM` lines to the latest version, e.g. `python:3.13-slim` -> `python:3.14-slim`.

## Automation

- `--commit` flag: commit each upgraded file separately, with a commit message describing the upgrade.

## Project

- CI (GitHub Actions) running `make check` on pull requests and push, on Linux and macOS.
- Publish releases to PyPI on tags, using a GitHub Actions workflow.
- Publish the docker image to ghcr.io on tags.
- Tag v0.1.0, so versions from setuptools-scm look reasonable.
- Add the npm CLI to the Dockerfile when the package.json / package-lock.json upgraders land.
