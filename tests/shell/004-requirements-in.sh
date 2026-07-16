#!/bin/bash

set -e
set -x

testdir="$(pwd)/out/shell-tests/004-requirements-in"
rm -rf "$testdir"
mkdir -p "$testdir"
cd "$testdir"

# Set up a "repo" using the requirements.in -> requirements.txt workflow,
# compiled as if it were 2023, so an upgrade is guaranteed to be available:
echo 'packaging>=20' > requirements.in
uv pip compile --exclude-newer 2023-01-01T00:00:00Z requirements.in -o requirements.txt
old="$(grep '^packaging==' requirements.txt)"
test -n "$old"

updee

# The exact new version is not deterministic, but it must have changed:
new="$(grep '^packaging==' requirements.txt)"
test -n "$new"
test "$old" != "$new"

# It must have been recompiled from requirements.in, and still be valid:
grep -q 'requirements.in' requirements.txt
uv pip compile requirements.in > /dev/null
