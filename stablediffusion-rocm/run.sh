#!/bin/bash
source ../utils.sh
python_exec=venv/bin/python3.10

# Main function
main() {
    # Create virtual environment
    use_venv

    # Prints ROCM info with available GPUs
    rocm-smi

    # Start SD
    TORCH_BLAS_PREFER_HIPBLASLT=0 $python_exec webui/launch.py --listen --enable-insecure-extension-access --opt-split-attention

}

main
