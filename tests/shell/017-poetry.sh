#!/bin/bash

set -e
set -x

testdir="$(pwd)/out/shell-tests/017-poetry"
rm -rf "$testdir"
mkdir -p "$testdir"
cd "$testdir"

# A poetry-managed pyproject.toml should be skipped with a clear message:
cat > pyproject.toml <<'EOF'
[tool.poetry]
name = "shelltest"
version = "0.1.0"

[tool.poetry.dependencies]
python = "^3.10"
packaging = ">=20"
EOF
cp pyproject.toml pyproject.toml.orig

updee | tee output.log

grep -q "poetry" output.log
grep -E -q "pyproject.toml +skipped" output.log
cmp pyproject.toml.orig pyproject.toml
