#!/bin/bash

# Script to set up virtual environment and install dependencies
# This script can be run from any directory

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Change to the script's directory to ensure relative paths work correctly
cd "$SCRIPT_DIR/.."

# Exit on any error
set -e

if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
else
    echo "Virtual environment already exists."
fi

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies from requirements.txt..."
pip install -r requirements.txt

if [ -f "requirements-dev.txt" ]; then
    echo "Installing development dependencies from requirements-dev.txt..."
    pip install -r requirements-dev.txt
fi

echo "Setup complete!"
