#!/bin/bash

# Script to run the Flask application using the virtual environment

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Change to the script's parent directory
cd "$SCRIPT_DIR/.." || exit

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Virtual environment not found. Please run setup.sh first."
    exit 1
fi

# Activate virtual environment
echo "Activating virtual environment..."
# shellcheck source=/dev/null
source .venv/bin/activate

# Run the Flask application
echo "Starting Flask application..."
export PYTHONPATH=src
python -m mtv_dl_web.app
