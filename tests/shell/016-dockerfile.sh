#!/bin/bash

set -e
set -x

testdir="$(pwd)/out/shell-tests/016-dockerfile"
rm -rf "$testdir"
mkdir -p "$testdir"
cd "$testdir"

# Set up a "repo" with a Dockerfile using old base images:
cat > Dockerfile <<'EOF'
FROM python:3.9-slim AS builder
RUN echo build

FROM ubuntu:20.04
COPY --from=builder /app /app
EOF

updee

# The version tags must have been bumped, keeping their shape:
! grep -q 'python:3.9-slim' Dockerfile
grep -E -q '^FROM python:3\.[0-9]+-slim AS builder$' Dockerfile
! grep -q 'ubuntu:20.04' Dockerfile
grep -E -q '^FROM ubuntu:[0-9]+\.[0-9]+$' Dockerfile

# The rest of the file must be untouched:
grep -q 'RUN echo build' Dockerfile
grep -q 'COPY --from=builder /app /app' Dockerfile
