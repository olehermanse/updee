#!/bin/bash

set -e
set -x

testdir="$(pwd)/out/shell-tests/009-summary"
rm -rf "$testdir"
mkdir -p "$testdir"
cd "$testdir"

echo 'packaging>=20' > requirements.txt
echo '{}' > package.json

# One line per file, with its status:
updee --dry-run | grep -q "Summary:"
updee --dry-run | grep -E -q "requirements.txt +would upgrade"
updee --dry-run | grep -E -q "package.json +skipped"
