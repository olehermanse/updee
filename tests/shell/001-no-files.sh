#!/bin/bash

set -e
set -x

testdir="$(pwd)/out/shell-tests/001-no-files"
rm -rf "$testdir"
mkdir -p "$testdir"
cd "$testdir"

# In an empty "repo" there is nothing to upgrade - expect failure and a message
! upd
upd | grep -q "No files to upgrade found"
