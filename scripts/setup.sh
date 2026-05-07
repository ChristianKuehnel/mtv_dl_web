#!/bin/bash

# MTV Downloader Web Interface Setup Script
# This script checks for required development tools and installs them if missing

set -e  # Exit on any error

# Set root directory to the parent directory of this script
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# Set virtual environment directory
VENV_DIR="$ROOT_DIR/venv"
# Set node modules directory
NODE_MODULES="$ROOT_DIR/node_modules"

echo "Setting up development environment for MTV Downloader Web Interface..."

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to install Debian packages
install_debian_packages() {
    echo "Installing Debian packages..."
    apt-get update
    apt-get install -y "$@"
}

# Function to create and activate Python virtual environment
setup_python_env() {
    echo "Setting up Python virtual environment..."
    
    # Check if Python 3.10+ is available
    if ! command_exists python3; then
        echo "Python 3 not found. Installing Python 3..."
        install_debian_packages python3 python3-pip python3-venv
    fi
    
    # Create virtual environment in project root
    if [ ! -d "$VENV_DIR" ]; then
        python3 -m venv "$VENV_DIR"
        echo "Virtual environment created in project root."
    else
        echo "Virtual environment already exists in project root."
    fi
    
    # Activate virtual environment (suppress SC1091 warning as activation is intentional)
    # shellcheck disable=SC1091
    source "$VENV_DIR/bin/activate"
    
    # Upgrade pip
    pip install --upgrade pip
    
    echo "Python environment ready."
}

# Function to install Python packages using uv
install_python_packages() {
    echo "Installing Python packages with uv..."
    # shellcheck disable=SC1091
    source "$VENV_DIR/bin/activate"
    
    # Install uv if not present
    if ! command_exists uv; then
        echo "Installing uv..."
        pip install uv
    fi
    
    # Install main dependencies (from pyproject.toml)
    echo "Installing main project dependencies..."
    uv sync --all-extras
    
    # Install dev dependencies
    echo "Installing development dependencies..."
    uv sync --extra=dev
    
    echo "Python packages installed with uv."
}

# Function to install Node.js and npm packages (for frontend formatting)
install_frontend_tools() {
    echo "Installing frontend development tools..."
    
    # Check if Node.js is installed
    if ! command_exists node; then
        echo "Node.js not found. Installing Node.js..."
        install_debian_packages nodejs npm
    else
        echo "Node.js already installed."
    fi
    
    # Install Prettier locally for HTML/JS formatting
    if ! command_exists prettier; then
        echo "Installing Prettier..."
        # Install to node_modules directory in project root
        mkdir -p "$NODE_MODULES"
        npm install --prefix "$ROOT_DIR" prettier
    else
        echo "Prettier already installed."
    fi
    
    echo "Frontend tools installed."
}

# Function to install Docker-related tools
install_container_tools() {
    echo "Checking container tools..."
    
    # Check for Podman (primary container runtime)
    if ! command_exists podman; then
        echo "Podman not found. Installing Podman..."
        install_debian_packages podman
    else
        echo "Podman already installed."
    fi

    # Check for hadolint (Dockerfile linter)
    if ! command_exists hadolint; then
        echo "Checking hadolint installation..."
        # Create a simple Dockerfile for testing
        TEST_DOCKERFILE="$ROOT_DIR/test_dockerfile"
        echo "FROM alpine:latest" > "$TEST_DOCKERFILE"
        echo "RUN echo 'test'" >> "$TEST_DOCKERFILE"
        
        # Try to run hadolint on the test file
        if command_exists podman; then
            echo "Testing hadolint with podman..."
            podman run --rm -i hadolint/hadolint < "$TEST_DOCKERFILE" 2>/dev/null && echo "hadolint test successful"
        else
            echo "hadolint not found. Please install with: sudo apt-get install hadolint"
        fi
        
        # Clean up test file
        rm -f "$TEST_DOCKERFILE"
        echo "hadolint can be run as: podman run --rm -i hadolint/hadolint < Dockerfile"
    else
        echo "hadolint already installed."
    fi
    
    echo "Container tools installed."
}

# Function to check and install mtv_dl
setup_mtv_dl() {
    echo "Setting up MTV DL dependency..."
    
    # Check if mtv_dl is already available
    if [ -d "src/mtv_dl" ]; then
        echo "mtv_dl directory found in src/mtv_dl."
        # Check if it's a git submodule
        if [ -f ".gitmodules" ] && grep -q "mtv_dl" .gitmodules; then
            echo "mtv_dl is configured as git submodule."
        else
            echo "mtv_dl exists but not as submodule. Checking if it's a proper clone..."
            if [ -d ".git" ] && [ -f "src/mtv_dl/pyproject.toml" ]; then
                echo "mtv_dl looks like a valid clone."
            else
                echo "Warning: mtv_dl directory found but doesn't appear to be a proper mtv_dl clone."
            fi
        fi
    else
        echo "mtv_dl not found. Cloning from upstream..."
        git submodule update --init --recursive
    fi
    
    # Install mtv_dl dependencies with uv
    echo "Installing mtv_dl dependencies..."
    if [ -f "src/mtv_dl/pyproject.toml" ]; then
        (
            cd src/mtv_dl
            # Install mtv_dl dev dependencies with uv
            uv sync --extra=dev
        )
    fi
    
    echo "mtv_dl setup complete."
}

# Main setup process
main() {
    echo "Starting setup for MTV Downloader Web Interface..."
    
    # Check for required tools
    echo "Checking required tools..."
    
    # Check for basic tools
    if ! command_exists git; then
        echo "Git not found. Installing..."
        install_debian_packages git
    fi
    
    # Setup Python environment
    setup_python_env
    
    # Install Python packages with uv
    install_python_packages
    
    # Install frontend tools (Prettier)
    install_frontend_tools
    
    # Install container tools
    install_container_tools
    
    # Setup mtv_dl dependency
    setup_mtv_dl
    
    echo "Setup complete!"
    echo ""
    echo "Next steps:"
    echo "1. Activate the virtual environment: source $VENV_DIR/bin/activate"
    echo "2. Run tests: pytest"
    echo "3. Start development server: uvicorn src.main:app --reload"
    echo "4. For container deployment: docker build -t mtv_dl_web ."
}

# Run main function
main