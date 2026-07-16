#!/usr/bin/env bash

set -e

echo "These tests expect upd to be installed globally or in venv"

echo "Looking for upd:"
command -v upd

echo "Check that test files are in expected location:"
ls -al tests/shell/*.sh

rm -rf out/shell-tests
mkdir -p out/shell-tests

# Run upd through coverage.py so shell tests also produce test coverage.
# Each invocation writes a separate data file (--parallel-mode), combined
# into out/shell-tests/.coverage after the tests.
root="$(pwd)"
export COVERAGE_RCFILE="$root/pyproject.toml"
export COVERAGE_FILE="$root/out/shell-tests/.coverage"
mkdir -p out/shell-tests/bin
cat > out/shell-tests/bin/upd <<'EOF'
#!/usr/bin/env bash
exec coverage run --parallel-mode -m upd "$@"
EOF
chmod +x out/shell-tests/bin/upd
export PATH="$root/out/shell-tests/bin:$PATH"

echo "Run shell tests:"
for file in tests/shell/*.sh; do
  bash $file
  echo "OK: $file"
done

echo "Shell test coverage:"
coverage combine
coverage report

echo "All shell tests successful!"
