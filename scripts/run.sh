#!/bin/bash

# Script to run the MTV Downloader Web service using uv
# This script will use the config.yaml file in the current directory

set -e  # Exit on any error

echo "Starting MTV Downloader Web service..."

# Check if uv is available
if ! command -v uv &> /dev/null; then
    echo "Error: uv is not installed or not in PATH"
    echo "Please install uv first: https://docs.astral.sh/uv/"
    exit 1
fi

# Check if config.yaml exists in current directory
if [ ! -f "config.yaml" ]; then
    echo "Warning: config.yaml not found in current directory"
    echo "Using default configuration values"
fi

# Activate the project environment
uv sync

# Run the service with uvicorn
uv run uvicorn mtv_dl_web.main:app --host 0.0.0.0 --port 8000

echo "Service stopped"