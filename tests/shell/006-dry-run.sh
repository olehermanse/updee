#!/bin/bash

set -e
set -x

testdir="$(pwd)/out/shell-tests/006-dry-run"
rm -rf "$testdir"
mkdir -p "$testdir"
cd "$testdir"

echo 'packaging>=20' > requirements.txt

upd --dry-run
upd --dry-run | grep -q "would run"

# The file must not have been changed:
grep -q '^packaging>=20$' requirements.txt
