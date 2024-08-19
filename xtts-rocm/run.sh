#!/bin/bash
source ../utils.sh
python_exec=venv/bin/python3.10

# Main function
main() {
    # Create virtual environment
    use_venv

    # Prints ROCM info with available GPUs
    rocm-smi

    # Start XTTS
    cd webui/
    TORCH_BLAS_PREFER_HIPBLASLT=0 ../$python_exec app.py --host 0.0.0.0 -v v2.0.3
}

main