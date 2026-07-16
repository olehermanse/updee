#!/bin/bash

set -e
set -x

testdir="$(pwd)/out/shell-tests/005-help-version"
rm -rf "$testdir"
mkdir -p "$testdir"
cd "$testdir"

upd --help
upd --help | grep -q "usage"
upd --help | grep -q -- "--version"

# The exact version is not deterministic, but it must be non-empty:
upd --version
test -n "$(upd --version)"
test -n "$(upd -V)"
