#!/bin/bash

# R2H5 Setup Script using UV
echo "Setting up R2H5 with UV package manager..."

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "UV is not installed. Installing UV..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    source ~/.bashrc
fi

# Check if ROOT is available (required dependency)
if ! command -v root &> /dev/null; then
    echo "WARNING: ROOT framework not found!"
    echo "Please install ROOT before proceeding:"
    echo "  - Conda: conda install -c conda-forge root"
    echo "  - System: apt-get install root-system (Ubuntu/Debian)"
    echo "  - From source: https://root.cern/install/build_from_source/"
    echo ""
    read -p "Do you want to continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Create virtual environment with Python 3.9
echo "Creating virtual environment..."
uv venv --python 3.9

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
uv pip install -r requirements.txt

# Install r2h5 package in development mode
echo "Installing r2h5 package in development mode..."
uv pip install -e .

echo ""
echo "Setup complete!"
echo "To activate the environment in the future, run:"
echo "  source .venv/bin/activate"
echo ""
echo "To verify installation, try:"
echo "  r2h5 --help"
