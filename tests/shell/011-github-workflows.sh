#!/bin/bash

set -e
set -x

testdir="$(pwd)/out/shell-tests/011-github-workflows"
rm -rf "$testdir"
mkdir -p "$testdir"
cd "$testdir"

# Set up a "repo" with a workflow pinning ancient action versions:
mkdir -p .github/workflows
cat > .github/workflows/ci.yml <<'EOF'
name: CI
on: push
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v1
      - uses: actions/setup-python@v1
        with:
          python-version: "3.12"
      - run: echo test
EOF
cp .github/workflows/ci.yml original.yml

updee

# v1 is ancient, so both actions must have been upgraded:
! cmp -s original.yml .github/workflows/ci.yml
! grep -Eq 'uses: actions/checkout@v1$' .github/workflows/ci.yml
! grep -Eq 'uses: actions/setup-python@v1$' .github/workflows/ci.yml

# The refs must still be major version tags (same precision as before):
grep -Eq '^      - uses: actions/checkout@v[0-9]+$' .github/workflows/ci.yml
grep -Eq '^      - uses: actions/setup-python@v[0-9]+$' .github/workflows/ci.yml

# The rest of the file must be untouched:
grep -q 'python-version: "3.12"' .github/workflows/ci.yml
grep -q 'runs-on: ubuntu-latest' .github/workflows/ci.yml
grep -q 'run: echo test' .github/workflows/ci.yml
