#!/bin/bash
source ../utils.sh
python_exec=venv/bin/python3.10

# Function to install StableDiffusion
install_stablediffusion() {
    if [ -d "webui" ]; then
        echo "StableDiffusion repository already exists. Skipping clone."
    else
        echo "Cloning StableDiffusion repository..."
        git clone -b dev https://github.com/AUTOMATIC1111/stable-diffusion-webui webui
    fi
    echo "Running StableDiffusion setup..."
    $python_exec webui/launch.py --skip-torch-cuda-test --exit
}

# Main function
main() {
    prepare_env

    # Install StableDiffusion
    install_stablediffusion

    clean

    echo "StableDiffusion installation complete."
}

# Run main function
main
