#!/bin/bash

# Function to check if PyTorch is installed
check_pytorch_installed() {
    python -c "import torch" >/dev/null 2>&1
    return $?
}

# Function to create virtual environment
create_venv() {
    if [ -d "venv" ]; then
        echo "Virtual environment already exists. Skipping creation."
        source venv/bin/activate
    else
        echo "Creating virtual environment..."
        python3.10 -m venv --system-site-packages venv
        source venv/bin/activate
        python3.10 -m pip install --upgrade pip
    fi
}

use_venv() {
    echo "Connecting to virtual environment..."
    source venv/bin/activate
}

# Function to install build-essential or equivalent
install_build_essentials() {
    echo "Checking for build essentials..."
    if [ -f /etc/debian_version ]; then
        sudo apt-get update
        sudo apt-get install -y build-essential python3.10-dev
    elif [ -f /etc/fedora-release ]; then
        if dnf list installed @development-tools &>/dev/null; then
            echo "Development Tools are already installed."
        else
            echo "Installing Development Tools..."
            sudo dnf groupinstall -y "Development Tools"
            sudo dnf install python3.10-devel
        fi
    else
        echo "Unsupported operating system. Please install build-essential or equivalent manually."
        exit 1
    fi
}

# Function to install PyTorch in the virtual environment
install_pytorch() {    
    # Check if PyTorch is installed
    if check_pytorch_installed; then
        echo "PyTorch is already installed."
    else
        echo "Installing PyTorch..."
        python3.10 -m pip install --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/rocm6.1
    fi
}

prepare_env(){
    # Create virtual environment
    create_venv

    # Install build essentials
    install_build_essentials

    # Install PyTorch in the virtual environment
    install_pytorch
}

clean() {
    python3.10 -m pip cache purge
}