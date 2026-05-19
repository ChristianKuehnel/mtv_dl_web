#!/bin/bash

# Script to remove the project's virtual environment
# This script can be run from any directory

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Change to the project root
cd "$SCRIPT_DIR/.."

# Exit on any error
set -e

if [ -d ".venv" ]; then
    echo "Removing virtual environment..."
    rm -rf .venv
    echo "Virtual environment removed."
else
    echo "Virtual environment does not exist."
fi
