#!/bin/bash

set -e
set -x

command -v npm >/dev/null || { echo "SKIP: npm is not installed"; exit 0; }

testdir="$(pwd)/out/shell-tests/012-package-lock"
rm -rf "$testdir"
mkdir -p "$testdir"
cd "$testdir"

# Set up a "repo" with a lockfile pinning an old version inside a ^5 range:
echo '{"name":"shelltest","version":"1.0.0"}' > package.json
npm install --package-lock-only --save semver@5.0.0
grep -q '"version": "5.0.0"' package-lock.json
cp package.json package.json.orig

updee --only package-lock.json

# npm update must have moved semver within the ^5 range:
! grep -q '"version": "5.0.0"' package-lock.json
grep -E -q '"version": "5\.[0-9]+\.[0-9]+"' package-lock.json

# package.json itself (the range) must be untouched:
cmp package.json.orig package.json

# The lockfile must still be valid and in sync with package.json:
npm install --package-lock-only
grep -E -q '"version": "5\.[0-9]+\.[0-9]+"' package-lock.json
