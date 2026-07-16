#!/bin/bash

set -e
set -x

command -v npm >/dev/null || { echo "SKIP: npm is not installed"; exit 0; }

testdir="$(pwd)/out/shell-tests/013-package-json"
rm -rf "$testdir"
mkdir -p "$testdir"
cd "$testdir"

# Set up a "repo" depending on an old major version of semver:
echo '{"name":"shelltest","version":"1.0.0"}' > package.json
npm install --package-lock-only --save semver@5.0.0
grep -E -q '"semver": ?"\^5\.0\.0"' package.json

updee --only package.json

# npm-check-updates must have bumped the range past ^5.0.0:
! grep -E -q '"semver": ?"\^5\.0\.0"' package.json
grep -E -q '"semver": ?"[~^]?[0-9]' package.json

# npm install must have brought the lockfile along:
! grep -q '"version": "5.0.0"' package-lock.json

# package.json and the lockfile must still be valid and in sync:
node -e 'require("./package.json")'
npm install --package-lock-only
