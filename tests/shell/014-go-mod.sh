#!/bin/bash

set -e
set -x

command -v go >/dev/null || { echo "SKIP: go is not installed"; exit 0; }

testdir="$(pwd)/out/shell-tests/014-go-mod"
rm -rf "$testdir"
mkdir -p "$testdir"
cd "$testdir"

# Set up a "repo" depending on an old version of a small module:
cat > go.mod <<'EOF'
module shelltest

go 1.21

require github.com/google/uuid v1.0.0
EOF
cat > main.go <<'EOF'
package main

import (
	"fmt"

	"github.com/google/uuid"
)

func main() {
	fmt.Println(uuid.New())
}
EOF
go mod tidy
grep -q 'github.com/google/uuid v1.0.0' go.mod

updee

# The dependency must have been upgraded past v1.0.0:
! grep -q 'github.com/google/uuid v1.0.0' go.mod
grep -q 'github.com/google/uuid v' go.mod

# The module must still build:
go build ./...
