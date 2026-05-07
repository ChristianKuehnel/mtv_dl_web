#!/bin/bash

# MTV Downloader Web Interface - Linting and Formatting Script
# This script performs all code quality checks and formatting according to project conventions

set -e  # Exit on any error

# Set root directory to the parent directory of this script
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# Set virtual environment directory
VENV_DIR="$ROOT_DIR/venv"

echo "Running code quality checks and formatting..."

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to run Python formatting with black
run_black() {
    echo "Running Black formatter on Python files..."
    source "$VENV_DIR/bin/activate"
    black src/ scripts/
    echo "Python formatting complete."
}

# Function to run Python type checking with mypy
run_mypy() {
    echo "Running MyPy type checking..."
    source "$VENV_DIR/bin/activate"
    mypy src/ --ignore-missing-imports
    echo "Type checking complete."
}

# Function to run Dockerfile linting with hadolint
run_hadolint() {
    echo "Running hadolint on Dockerfile..."
    if command_exists hadolint; then
        hadolint Dockerfile
        echo "Dockerfile linting complete."
    else
        echo "Warning: hadolint not found. Skipping Dockerfile linting."
    fi
}

# Function to run HTML/JS formatting with Prettier
run_prettier() {
    echo "Running Prettier on HTML/JS files..."
    if command_exists prettier; then
        # Format HTML and JS files
        find src/ -name "*.html" -o -name "*.js" | xargs prettier --write
        echo "HTML/JS formatting complete."
    else
        echo "Warning: Prettier not found. Skipping HTML/JS formatting."
    fi
}

# Function to run ShellCheck on shell scripts
run_shellcheck() {
    echo "Running ShellCheck on shell scripts..."
    if command_exists shellcheck; then
        # Check all shell scripts in scripts directory
        find scripts/ -name "*.sh" -type f | xargs shellcheck
        echo "ShellCheck complete."
    else
        echo "Error: ShellCheck not found. Please run setup script to install all dependencies."
        exit 1
    fi
}

# Function to run all checks
run_all_checks() {
    echo "Starting comprehensive code quality checks..."
    
    # Run all formatting and linting checks
    run_black
    run_mypy
    run_hadolint
    run_prettier
    run_shellcheck
    
    echo "All code quality checks completed successfully!"
    echo ""
    echo "Summary:"
    echo "- Python code formatted with Black"
    echo "- Python types checked with MyPy"
    echo "- Dockerfile linted with hadolint"
    echo "- HTML/JS formatted with Prettier"
    echo "- Shell scripts checked with ShellCheck"
}

# Main execution
main() {
    # Check if virtual environment exists
    if [ ! -d "$VENV_DIR" ]; then
        echo "Error: Virtual environment not found at $VENV_DIR."
        echo "Please run setup script first: ./scripts/setup.sh"
        exit 1
    fi
    
    # Run all checks
    run_all_checks
}

# Run main function
main