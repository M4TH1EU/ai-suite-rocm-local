#!/bin/bash
source ../utils.sh
python_exec="$(pwd)/venv/bin/python3.10"

# Function to install StableDiffusion
install_background_remover() {
    echo "Cloning webui..."
    git clone ssh://git@git.broillet.ch:222/Clone/dis-background-removal.git webui
    
    echo "Installing requirements..."
    $python_exec -m pip install -r webui/requirements.txt
    
    echo "Cloning DIS repo"
    git clone ssh://git@git.broillet.ch:222/Clone/DIS.git tmp-dis
    mv tmp-dis/IS-Net/* webui/
    sudo rm -R tmp-dis
    
    echo "Finalizing..."
    mkdir webui/saved_models -p
    mv webui/isnet.pth webui/saved_models
    sudo rm -R webui/.git
    
}

# Main function
main() {
    prepare_env

    # Set it up
    install_background_remover

    clean

    echo "BackgroundRemover installation complete."
}

# Run main function
main
