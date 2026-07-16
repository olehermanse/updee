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
upd --dry-run | grep -q "Summary:"
upd --dry-run | grep -E -q "requirements.txt +would upgrade"
upd --dry-run | grep -E -q "package.json +skipped"
