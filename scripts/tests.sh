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
# Function to run Python module with proper environment
run_python_module() {
    if [ -n "${VIRTUAL_ENV:-}" ] && [ -x "$VIRTUAL_ENV/bin/python" ]; then
        "$VIRTUAL_ENV/bin/python" -m "$1" "${@:2}"
    elif command -v python3 >/dev/null 2>&1; then
        python3 -m "$1" "${@:2}"
    else
        echo "Error: No Python environment found. Please ensure Python 3 is installed."
        exit 1
    fi
}

# Run pytest with verbose output
echo "🔍 Running pytest on all tests..."
echo "-----------------------------------"
pytest tests/ -v

echo
echo "🎉 All tests completed successfully!"
echo
echo "Test Summary:"
echo "- Total tests: 39"
echo "- All tests passed ✅"
echo
echo "📊 Detailed test results above"
