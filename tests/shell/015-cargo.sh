#!/bin/bash

set -e
set -x

command -v cargo >/dev/null || { echo "SKIP: cargo is not installed"; exit 0; }

testdir="$(pwd)/out/shell-tests/015-cargo"
rm -rf "$testdir"
mkdir -p "$testdir"
cd "$testdir"

# Set up a "repo" with a lockfile pinning an old version inside the 0.2 range:
cat > Cargo.toml <<'EOF'
[package]
name = "shelltest"
version = "0.1.0"
edition = "2021"

[dependencies]
libc = "0.2"
EOF
mkdir src
touch src/lib.rs
cargo generate-lockfile
cargo update -p libc --precise 0.2.100
grep -A 1 'name = "libc"' Cargo.lock | grep -q 'version = "0.2.100"'
cp Cargo.toml Cargo.toml.orig

updee | tee output.log

# Cargo.toml is skipped in favor of the lockfile, which cargo update bumps:
grep -E -q "Cargo.toml +skipped" output.log
grep -E -q "Cargo.lock +upgraded" output.log
cmp Cargo.toml.orig Cargo.toml
grep -A 1 'name = "libc"' Cargo.lock | grep -q 'version = "0.2.'
! (grep -A 1 'name = "libc"' Cargo.lock | grep -q 'version = "0.2.100"')

# The lockfile must still be valid and up-to-date:
cargo update --locked
