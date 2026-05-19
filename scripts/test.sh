#!/bin/bash

# Run the Python test suite.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."

set -e

if [ ! -d ".venv" ]; then
    echo "Virtual environment not found. Please run scripts/setup.sh first."
    exit 1
fi

# shellcheck source=/dev/null
source .venv/bin/activate

echo "Running tests..."
python -m pytest tests
