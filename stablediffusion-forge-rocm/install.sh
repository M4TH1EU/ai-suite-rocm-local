#!/bin/bash
source ../utils.sh
python_exec=venv/bin/python3.10

# Function to install/update StableDiffusion
install_stablediffusionforge() {
    if [ -d "webui" ]; then
        echo "StableDiffusionForge repository already exists."
        yes_or_no "Do you want to update StableDiffusionForge WebUI ?" && {
            cd webui
            git pull
            echo "StableDiffusionForge WebUI successfully updated."
        }
    else
        echo "Cloning StableDiffusionForge repository..."
        git clone https://github.com/lllyasviel/stable-diffusion-webui-forge webui

        echo "Running StableDiffusionForge setup..."
        $python_exec webui/launch.py --skip-torch-cuda-test --exit

        ln -s webui/models models
        ln -s webui/outputs outputs
    fi

}

# Main function
main() {
    prepare_env

    # Install StableDiffusionForge
    install_stablediffusionforge

    clean

    echo "StableDiffusion installation/update complete. Use ./run.sh to start"
}

# Run main function
main
