#!/bin/bash

# MTV Downloader Web Interface - Linting and Formatting Script
# This script performs code quality checks and formatting according to project conventions.
# Use --check in CI to verify formatting without modifying files.

set -euo pipefail  # Exit on any error, undefined vars, pipe failures

# Set root directory to the parent directory of this script
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CHECK_MODE=false

usage() {
    cat <<EOF
Usage: $0 [--check]

Options:
  --check   Verify formatting and linting without modifying files.
  -h, --help
            Show this help message.
EOF
}

while [ "$#" -gt 0 ]; do
    case "$1" in
        --check)
            CHECK_MODE=true
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            echo "Error: Unknown argument: $1"
            usage
            exit 1
            ;;
    esac
    shift
done

if [ "$CHECK_MODE" = true ]; then
    echo "Running code quality checks..."
else
    echo "Running code quality checks and formatting..."
fi

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

run_python_module() {
    if command_exists uv; then
        (
            cd "$ROOT_DIR"
            uv run "$@"
        )
    else
        echo "Error: uv not found. Please install uv to run Python tools."
        exit 1
    fi
}

run_prettier_command() {
    if [ -x "$ROOT_DIR/node_modules/.bin/prettier" ]; then
        "$ROOT_DIR/node_modules/.bin/prettier" "$@"
    elif command_exists prettier; then
        prettier "$@"
    else
        echo "Error: Prettier not found. Run npm install before linting."
        exit 1
    fi
}

# Function to run Python formatting with black
run_black() {
    echo "Running Black on Python files..."
    # Check if first-party source directory exists before running black.
    if [ -d "$ROOT_DIR/src/mtv_dl_web" ]; then
        if [ "$CHECK_MODE" = true ]; then
            run_python_module black --check "$ROOT_DIR/src/mtv_dl_web/" "$ROOT_DIR/scripts/"
        else
            run_python_module black "$ROOT_DIR/src/mtv_dl_web/" "$ROOT_DIR/scripts/"
        fi
        echo "Black complete."
    else
        echo "Warning: src/mtv_dl_web directory not found. Skipping Python formatting."
    fi
}

# Function to run Python type checking with mypy
run_mypy() {
    echo "Running MyPy type checking..."
    # Check only first-party application code; src/mtv_dl is vendored upstream code.
    if [ -d "$ROOT_DIR/src/mtv_dl_web" ]; then
        run_python_module mypy "$ROOT_DIR/src/mtv_dl_web/" --ignore-missing-imports
        echo "Type checking complete."
    else
        echo "Warning: src/mtv_dl_web directory not found. Skipping type checking."
    fi
}

# Function to run Dockerfile linting with hadolint
run_hadolint() {
    echo "Running hadolint on Dockerfile..."
    if command_exists hadolint; then
        if [ -f "$ROOT_DIR/Dockerfile" ]; then
            hadolint "$ROOT_DIR/Dockerfile"
        else
            echo "Warning: Dockerfile not found. Skipping Dockerfile linting."
        fi
        echo "Dockerfile linting complete."
    elif command_exists podman; then
        if [ -f "$ROOT_DIR/Dockerfile" ]; then
            echo "Using podman to run hadolint..."
            podman run --rm -i ghcr.io/hadolint/hadolint < "$ROOT_DIR/Dockerfile"
        else
            echo "Warning: Dockerfile not found. Skipping Dockerfile linting."
        fi
        echo "Dockerfile linting complete."
    else
        echo "Error: hadolint not found. Install hadolint before linting."
        exit 1
    fi
}

# Function to run HTML/JS formatting with Prettier
run_prettier() {
    echo "Running Prettier on HTML/JS/CSS files..."
    if [ -d "$ROOT_DIR/src" ]; then
        mapfile -d '' prettier_files < <(find "$ROOT_DIR/src/" -type f \( -name "*.html" -o -name "*.js" -o -name "*.css" \) -print0)
        if [ "${#prettier_files[@]}" -eq 0 ]; then
            echo "No HTML/JS/CSS files found. Skipping Prettier."
        elif [ "$CHECK_MODE" = true ]; then
            run_prettier_command --check "${prettier_files[@]}"
        else
            run_prettier_command --write "${prettier_files[@]}"
        fi
        echo "Prettier complete."
    else
        echo "Warning: src directory not found. Skipping Prettier."
    fi
}

# Function to run ShellCheck on shell scripts
run_shellcheck() {
    echo "Running ShellCheck on shell scripts..."
    if command_exists shellcheck; then
        # Check all shell scripts in scripts directory
        find "$ROOT_DIR/scripts/" -name "*.sh" -type f -exec shellcheck {} +
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
    if [ "$CHECK_MODE" = true ]; then
        echo "- Python code formatting verified with Black"
        echo "- HTML/JS/CSS formatting verified with Prettier"
    else
        echo "- Python code formatted with Black"
        echo "- HTML/JS/CSS formatted with Prettier"
    fi
    echo "- Python types checked with MyPy"
    echo "- Dockerfile linted with hadolint"
    echo "- Shell scripts checked with ShellCheck"
}

# Main execution
main() {
    # Run all checks
    run_all_checks
}

# Run main function
main
