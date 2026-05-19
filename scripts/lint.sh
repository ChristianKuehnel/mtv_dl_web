#!/bin/bash

# Format code and run checks.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."

set -e

if [ ! -d ".venv" ]; then
    echo "Virtual environment not found. Please run scripts/setup.sh first."
    exit 1
fi

if [ ! -x "node_modules/.bin/prettier" ] || [ ! -x "node_modules/.bin/htmlhint" ]; then
    echo "HTML linting tools not found. Please run scripts/setup.sh first."
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
BLACK_NUM_WORKERS=1 python -m black "${paths[@]}"

echo "Running Prettier..."
node_modules/.bin/prettier --write src/mtv_dl_web/static/index.html

echo "Running HTMLHint..."
node_modules/.bin/htmlhint src/mtv_dl_web/static/index.html

echo "Running mypy..."
python -m mypy "${paths[@]}"
