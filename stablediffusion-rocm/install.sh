#!/bin/bash
source ../utils.sh
python_exec="$(pwd)/venv/bin/python3.10"

# Function to install/update StableDiffusion
install_stablediffusion() {
    if [ -d "webui" ]; then
        echo "StableDiffusion repository already exists."
        yes_or_no "Do you want to update StableDiffusion WebUI (dev branch) ?" && {
            cd webui
            git pull
            echo "StableDiffusion WebUI successfully updated."
        }
    else
        echo "Cloning StableDiffusion repository..."
        git clone -b dev https://github.com/AUTOMATIC1111/stable-diffusion-webui webui

        echo "Running StableDiffusion setup..."
        $python_exec webui/launch.py --skip-torch-cuda-test --exit

        ln -s webui/models models
        ln -s webui/outputs outputs
    fi

}

# Main function
main() {
    prepare_env

    # Install StableDiffusion
    install_stablediffusion

    clean

    echo "StableDiffusion installation/update complete. Use ./run.sh to start"
}

# Run main function
main
