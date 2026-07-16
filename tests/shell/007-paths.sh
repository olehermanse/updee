#!/bin/bash

set -e
set -x

testdir="$(pwd)/out/shell-tests/007-paths"
rm -rf "$testdir"
mkdir -p "$testdir"
cd "$testdir"

mkdir one two
echo 'packaging>=20' > one/requirements.txt
echo 'packaging>=20' > two/requirements.txt

# Only the given directory is considered:
updee --dry-run one | grep -q "one/requirements.txt"
! updee --dry-run one | grep -q "two/requirements.txt"

# A file can be given directly:
updee --dry-run two/requirements.txt | grep -q "two/requirements.txt"

# Nonexistent paths are an error:
! updee --dry-run three
