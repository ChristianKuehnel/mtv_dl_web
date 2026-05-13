#!/bin/bash

# MTV Downloader Web Interface - Test Suite Runner
# This script runs the entire test suite for the project

set -euo pipefail  # Exit on any error, undefined vars, pipe failures

# Set root directory to the parent directory of this script
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "🧪 Running MTV Downloader Web Interface Test Suite"
echo "=================================================="
echo

# Change to root directory
cd "$ROOT_DIR"

# Function to run tests with proper environment
run_tests() {
    if command -v uv >/dev/null 2>&1; then
        UV_BIN="uv"
    elif [ -x "$HOME/.local/bin/uv" ]; then
        UV_BIN="$HOME/.local/bin/uv"
    else
        echo "Error: uv is required to run the test suite."
        echo "Install uv, then run: uv sync --extra dev"
        exit 1
    fi

    echo "🔍 Running pytest with uv..."
    echo "-----------------------------------"
    "$UV_BIN" sync --extra dev
    "$UV_BIN" run --extra dev --with-editable . pytest tests/ -v
}

# Run tests
run_tests

echo
echo "🎉 All tests completed successfully!"
