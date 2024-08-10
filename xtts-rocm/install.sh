#!/bin/bash
source ../utils.sh
python_exec=venv/bin/python3.10

# Function to install/update StableDiffusion
install_xtts() {
    if [ -d "webui" ]; then
        echo "XTTS repository already exists. Skipping clone."
        yes_or_no "Do you want to update XTTS WebUI ?" && {
            cd webui
            git pull
            echo "XTTS WebUI successfully updated."
        }
    else
        echo "Cloning XTTS repository..."
        git clone https://github.com/daswer123/xtts-webui webui
        grep -v 'torch' requirements.txt > requirements_without_torch.txt
    fi

    $python_exec -m pip install -r webui/requirements_without_torch.txt

    # Disable gpu for faster-whipser as ROCM isn't supported yet
    sed -i 's/device = "cuda" if torch.cuda.is_available() else "cpu"/device = "cpu"/' webui/scripts/utils/formatter.py
    sed -i 's/asr_model = WhisperModel(whisper_model, device=device, compute_type="float16")/asr_model = WhisperModel(whisper_model, device=device, compute_type="int8")/' webui/scripts/utils/formatter.py

    # Deepspeed and ninja (not working)
    $python_exec -m pip install deepspeed ninja
    # apt-get install -y ninja-build
}

# Main function
main() {
    prepare_env

    # Install XTTS
    install_xtts

    clean

    echo "XTTS installation/update complete."
}

# Run main function
main
