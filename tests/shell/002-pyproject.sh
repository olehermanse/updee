#!/bin/bash

set -e
set -x

testdir="$(pwd)/out/shell-tests/002-pyproject"
rm -rf "$testdir"
mkdir -p "$testdir"
cd "$testdir"

# Set up a "repo" with a pyproject.toml:
cat > pyproject.toml <<'EOF'
[project]
name = "shelltest"
version = "0.1.0"
requires-python = ">=3.10"
dependencies = ["packaging>=20"]
EOF

# Lock as if it were 2023, so an upgrade is guaranteed to be available:
uv lock --exclude-newer 2023-01-01T00:00:00Z
old="$(grep -A 1 '^name = "packaging"' uv.lock | grep '^version')"
test -n "$old"

updee

# The exact new version is not deterministic, but it must have changed:
new="$(grep -A 1 '^name = "packaging"' uv.lock | grep '^version')"
test -n "$new"
test "$old" != "$new"

# The lockfile must still be valid and up-to-date:
uv lock --check
