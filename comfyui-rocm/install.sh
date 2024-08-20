#!/bin/bash
source ../utils.sh
python_exec=venv/bin/python3.10

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

        # Install manager
        cd webui/custom_nodes
        git clone https://github.com/ltdrdata/ComfyUI-Manager.git

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
