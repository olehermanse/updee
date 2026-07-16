#!/bin/bash

set -e
set -x

testdir="$(pwd)/out/shell-tests/008-only"
rm -rf "$testdir"
mkdir -p "$testdir"
cd "$testdir"

echo 'packaging>=20' > requirements.txt
echo '{}' > package.json

# Only the given file names are considered:
upd --dry-run --only requirements.txt | grep -q "requirements.txt"
! upd --dry-run --only requirements.txt | grep -q "package.json"

# Unknown file names are an error:
! upd --dry-run --only foo.txt
upd --dry-run --only foo.txt | grep -q "unknown file name"
