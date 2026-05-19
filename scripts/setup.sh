#!/bin/bash

# Script to set up virtual environment and install dependencies
# This script can be run from any directory

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Change to the script's directory to ensure relative paths work correctly
cd "$SCRIPT_DIR/.."

# Exit on any error
set -e

CONFIG_DIR="${MTV_DL_WEB_CONFIG_DIR:-$PWD/config}"
DOWNLOADS_DIR="${MTV_DL_WEB_DOWNLOADS_DIR:-$PWD/Downloads}"
DATABASE_DIR="${MTV_DL_WEB_DATABASE_DIR:-$PWD/mtv_dl_db}"

if ! command -v shellcheck >/dev/null 2>&1; then
    echo "ShellCheck is not installed. Please install shellcheck and run this script again."
    exit 1
fi

if ! command -v npm >/dev/null 2>&1; then
    echo "npm is not installed. Please install npm and run this script again."
    exit 1
fi

if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
else
    echo "Virtual environment already exists."
fi

echo "Creating local runtime directories..."
mkdir -p "$CONFIG_DIR" "$DOWNLOADS_DIR" "$DATABASE_DIR"

echo "Updating local runtime directory permissions..."
chmod -R u+rwX,go+rX "$CONFIG_DIR"
chmod -R u+rwX,go+rwX "$DOWNLOADS_DIR" "$DATABASE_DIR"

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

echo "Installing HTML linting tools..."
npm install --no-save prettier htmlhint

echo "Setup complete!"
