#!/bin/bash
source ../utils.sh
python_exec="$(pwd)/venv/bin/python3.10"

NAME="ComfyUI"

# Function to install/update
install() {
    if [ -d "webui" ]; then
        echo $NAME "is already installed. Updating..."
        yes_or_no "Do you want to update $NAME?" && {
            cd webui
            git pull
            echo "$NAME WebUI successfully updated."
        }

    else
        echo "Cloning $NAME repository..."
        git clone https://github.com/comfyanonymous/ComfyUI.git webui

        echo "Running $NAME setup..."
        $python_exec -m pip install -r webui/requirements.txt


        cd webui/custom_nodes

        # Install manager
        git clone https://github.com/ltdrdata/ComfyUI-Manager.git

        # Add GGUF support
        git clone https://github.com/city96/ComfyUI-GGUF
        $python_exec -m pip install --upgrade gguf numpy==1.26.4

        # Add NF4 support
        git clone https://github.com/comfyanonymous/ComfyUI_bitsandbytes_NF4.git
        $python_exec -m pip install --upgrade ../../../bitsandbytes-rocm-build/bitsandbytes-0.43.3.dev0-cp310-cp310-linux_x86_64.whl # install bitsandbytes for rocm until it is available on pypi

        ln -s webui/models models
    fi

}

# Main function
main() {
    prepare_env
    install
    clean
    echo "$NAME installation/update complete. Use ./run.sh to start"
}

# Run main function
main
