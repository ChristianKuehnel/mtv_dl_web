#!/bin/bash

# Script to set up virtual environment and install dependencies
# This script can be run from any directory

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Change to the script's directory to ensure relative paths work correctly
cd "$SCRIPT_DIR/.."

# Exit on any error
set -e

if ! command -v shellcheck >/dev/null 2>&1; then
    echo "ShellCheck is not installed. Please install shellcheck and run this script again."
    exit 1
fi

if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
else
    echo "Virtual environment already exists."
fi

# Activate virtual environment
echo "Activating virtual environment..."
# shellcheck source=/dev/null
source .venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing project with development dependencies..."
pip install -e ".[dev]"

echo "Setup complete!"
