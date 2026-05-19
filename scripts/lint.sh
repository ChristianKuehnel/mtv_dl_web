#!/bin/bash

# Run Python formatting and type checks.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."

set -e

if [ ! -d ".venv" ]; then
    echo "Virtual environment not found. Please run scripts/setup.sh first."
    exit 1
fi

# shellcheck source=/dev/null
source .venv/bin/activate

paths=("src")
if [ -d "tests" ]; then
    paths+=("tests")
fi

echo "Running ShellCheck..."
shellcheck scripts/*.sh

echo "Running Black..."
BLACK_NUM_WORKERS=1 python -m black --check "${paths[@]}"

echo "Running mypy..."
python -m mypy "${paths[@]}"
