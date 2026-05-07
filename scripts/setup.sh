#!/bin/bash

# MTV Downloader Web Interface Setup Script
# This script checks for required development tools and installs them if missing

set -e  # Exit on any error

# Set root directory to the parent directory of this script
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# Set virtual environment directory
VENV_DIR="$ROOT_DIR/venv"

echo "Setting up development environment for MTV Downloader Web Interface..."

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to install Debian packages
install_debian_packages() {
    echo "Installing Debian packages..."
    sudo apt-get update
    sudo apt-get install -y "$@"
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
    
    # Activate virtual environment
    source "$VENV_DIR/bin/activate"
    
    # Upgrade pip
    pip install --upgrade pip
    
    echo "Python environment ready."
}

# Function to install Python packages in virtual environment
install_python_packages() {
    echo "Installing Python packages..."
    source "$VENV_DIR/bin/activate"
    
    # Install required Python packages from requirements file
    if [ -f "$ROOT_DIR/requirements-dev.txt" ]; then
        pip install -r "$ROOT_DIR/requirements-dev.txt"
        echo "Python packages installed from requirements-dev.txt."
    else
        # Fallback to installing packages directly
        pip install fastapi uvicorn pydantic python-dotenv
        pip install pytest mypy black 
        pip install pre-commit  # For git hooks
        pip install pytest-cov pytest-asyncio
        pip install httpx
        pip install types-requests
        echo "Python packages installed directly."
    fi
    
    echo "Python packages installed."
}

# Function to install Python packages in virtual environment
install_python_packages() {
    echo "Installing Python packages..."
    source venv/bin/activate
    
    # Install required Python packages from requirements file
    if [ -f "requirements-dev.txt" ]; then
        pip install -r requirements-dev.txt
        echo "Python packages installed from requirements-dev.txt."
    fi
    
    echo "Python packages installed."
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
    
    # Install Prettier globally for HTML/JS formatting
    if ! command_exists prettier; then
        echo "Installing Prettier..."
        npm install -g prettier
    else
        echo "Prettier already installed."
    fi
    
    echo "Frontend tools installed."
}

# Function to install Docker-related tools
install_container_tools() {
    echo "Checking container tools..."
    
    # Check for Docker
    if ! command_exists docker; then
        echo "Docker not found. Installing Docker..."
        # Install Docker using official script
        curl -fsSL https://get.docker.com -o get-docker.sh
        sudo sh get-docker.sh
        sudo usermod -aG docker $USER
        rm get-docker.sh
    else
        echo "Docker already installed."
    fi
    
    # Check for Podman
    if ! command_exists podman; then
        echo "Podman not found. Installing Podman..."
        install_debian_packages podman
    else
        echo "Podman already installed."
    fi
    
    # Check for Docker Compose
    if ! command_exists docker-compose; then
        echo "Docker Compose not found. Installing..."
        # Try to install via apt first
        install_debian_packages docker-compose
    else
        echo "Docker Compose already installed."
    fi
    
    # Check for hadolint (Dockerfile linter)
    if ! command_exists hadolint; then
        echo "Installing hadolint..."
        # Install hadolint using the official method
        sudo wget -O /usr/local/bin/hadolint https://github.com/hadolint/hadolint/releases/latest/download/hadolint-Linux-x86_64
        sudo chmod +x /usr/local/bin/hadolint
    else
        echo "hadolint already installed."
    fi
    
    echo "Container tools installed."
}

# Function to check and install mtv_dl
setup_mtv_dl() {
    echo "Setting up MTV DL dependency..."
    
    # Check if mtv_dl is already available
    if [ -d "mtv_dl" ]; then
        echo "mtv_dl directory found."
        # Check if it's a git submodule
        if [ -f ".gitmodules" ] && grep -q "mtv_dl" .gitmodules; then
            echo "mtv_dl is configured as git submodule."
        else
            echo "mtv_dl exists but not as submodule. Checking if it's a proper clone..."
            if [ -d ".git" ] && [ -f "mtv_dl/pyproject.toml" ]; then
                echo "mtv_dl looks like a valid clone."
            else
                echo "Warning: mtv_dl directory found but doesn't appear to be a proper mtv_dl clone."
            fi
        fi
    else
        echo "mtv_dl not found. Cloning from upstream..."
        git submodule update --init --recursive
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
    
    # Install Python packages
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
    echo "1. Activate the virtual environment: source venv/bin/activate"
    echo "2. Run tests: pytest"
    echo "3. Start development server: uvicorn src.main:app --reload"
    echo "4. For container deployment: docker build -t mtv_dl_web ."
}

# Run main function
main