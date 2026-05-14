#!/bin/bash

# MTV Downloader Web Interface Setup Script
# This script checks for required development tools and installs them if missing

set -e  # Exit on any error

# Set root directory to the parent directory of this script
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
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

# Function to install Python packages using uv
install_python_packages() {
    echo "Installing Python packages with uv..."
    
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

# Function to install git pre-commit hook that runs linting
install_git_precommit_hook() {
    echo "Installing git pre-commit hook..."
    
    # Determine the correct git directory
    GIT_DIR="/home/opencode/mtv_dl_web/.git"
    HOOKS_DIR="$GIT_DIR/hooks"
    
    # Create hooks directory if it doesn't exist
    mkdir -p "$HOOKS_DIR"
    
    # Create the pre-commit hook
    cat > "$HOOKS_DIR/pre-commit" << 'EOF'
#!/bin/bash

# Pre-commit hook to run linting checks before allowing commit

echo "Running linting checks before commit..."

# Run the linting script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LINTING_SCRIPT="$SCRIPT_DIR/scripts/linting.sh"

if [ -x "$LINTING_SCRIPT" ]; then
    echo "Running linting checks..."
    "$LINTING_SCRIPT" --check
    if [ $? -eq 0 ]; then
        echo "Linting checks passed."
        exit 0
    else
        echo "Linting checks failed. Please fix issues before committing."
        exit 1
    fi
else
    echo "Warning: Linting script not found or not executable"
    exit 0  # Allow commit to proceed if linting script isn't there
fi
EOF

    # Make the hook executable
    chmod +x "$HOOKS_DIR/pre-commit"
    
    echo "Git pre-commit hook installed successfully!"
    echo "The hook will now run linting checks before every commit."
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
    
    # Install Python packages with uv
    install_python_packages
    
    # Install frontend tools (Prettier)
    install_frontend_tools
    
    # Install container tools
    install_container_tools
    
    # Install git pre-commit hook
    install_git_precommit_hook
    
    echo "Setup complete!"
    echo ""
    echo "Next steps:"
    echo "1. Run tests: pytest"
    echo "2. Start development server: uvicorn src.main:app --reload"
    echo "3. For container deployment: docker build -t mtv_dl_web ."
}

# Run main function
main