#!/usr/bin/env bash

set -e

echo "These tests expect upd to be installed globally or in venv"

echo "Looking for upd:"
command -v upd

echo "Check that test files are in expected location:"
ls -al tests/shell/*.sh

rm -rf out/shell-tests
mkdir -p out/shell-tests

echo "Run shell tests:"
for file in tests/shell/*.sh; do
  bash $file
  echo "OK: $file"
done

echo "All shell tests successful!"
