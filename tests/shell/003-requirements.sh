#!/bin/bash

set -e
set -x

testdir="$(pwd)/out/shell-tests/003-requirements"
rm -rf "$testdir"
mkdir -p "$testdir"
cd "$testdir"

# Set up a "repo" with a loose requirements.txt:
echo 'packaging>=20' > requirements.txt

updee

# The exact version is not deterministic, but it must now be pinned:
grep -q '^packaging==' requirements.txt
! grep -q '^packaging>=20$' requirements.txt

# The file must still be valid (resolvable):
uv pip compile requirements.txt > /dev/null
