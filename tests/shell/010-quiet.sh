#!/bin/bash

set -e
set -x

testdir="$(pwd)/out/shell-tests/010-quiet"
rm -rf "$testdir"
mkdir -p "$testdir"
cd "$testdir"

echo 'packaging>=20' > requirements.txt

output="$(updee --quiet 2>&1)"

# Only the summary - no progress lines, no uv output:
echo "$output" | grep -q "Summary:"
! echo "$output" | grep -q "running"
! echo "$output" | grep -q "Resolved"

# The upgrade still happened:
grep -q '^packaging==' requirements.txt
