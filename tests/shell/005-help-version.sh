#!/bin/bash

set -e
set -x

testdir="$(pwd)/out/shell-tests/005-help-version"
rm -rf "$testdir"
mkdir -p "$testdir"
cd "$testdir"

updee --help
updee --help | grep -q "usage"
updee --help | grep -q -- "--version"

# The exact version is not deterministic, but it must be non-empty:
updee --version
test -n "$(updee --version)"
test -n "$(updee -V)"
