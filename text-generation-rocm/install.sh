#!/bin/bash
source ../utils.sh
python_exec="$(pwd)/venv/bin/python3.10"

NAME="TextGeneration"

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
        # Add BnB
        $python_exec -m pip install --upgrade ../bitsandbytes-rocm-build/bitsandbytes-0.43.3.dev0-cp310-cp310-linux_x86_64.whl # install bitsandbytes for rocm until it is available on pypi

        # Add AutoGPTQ
        $python_exec -m pip install auto-gptq[triton] --no-build-isolation --extra-index-url https://huggingface.github.io/autogptq-index/whl/rocm573/

        # Add LlamaCPP
        CMAKE_ARGS="-DLLAMA_CLBLAST=on" FORCE_CMAKE=1 $python_exec -m pip install llama-cpp-python
        # CMAKE_ARGS="-DGGML_HIPBLAS=on" FORCE_CMAKE=1 $python_exec -m pip install llama-cpp-python

        # Add Triton
#        git clone https://github.com/ROCmSoftwarePlatform/triton.git .tritonrocm
#        cd .tritonrocm/python
#        $python_exec -m pip install ninja cmake; # build time dependencies
#        $python_exec -m pip uninstall triton -y && $python_exec -m pip install -e .
#        cd .. && sudo rm -R .tritonrocm

        echo "Cloning $NAME repository..."
        git clone https://github.com/oobabooga/text-generation-webui.git webui

        echo "Running $NAME setup..."

        # For some reasons theses want to reinstall torch for nvidia instead of using the download for rocm so manually install them
        sed -i '/accelerate/d' webui/requirements_amd.txt
        sed -i '/lm_eval/d' webui/requirements_amd.txt
        sed -i '/optimum/d' webui/requirements_amd.txt
        sed -i '/autoawq/d' webui/requirements_amd.txt

        $python_exec -m pip install -r webui/requirements_amd.txt

        $python_exec -m pip install accelerate # only works after requirements_amd.txt is installed ??!
        $python_exec -m pip install lm_eval optimum autoawq
        $python_exec -m pip install https://github.com/casper-hansen/AutoAWQ_kernels/releases/download/v0.0.7/autoawq_kernels-0.0.7+rocm571-cp310-cp310-linux_x86_64.whl --no-deps
        $python_exec -m pip install https://github.com/casper-hansen/AutoAWQ/releases/download/v0.2.6/autoawq-0.2.6-cp310-cp310-linux_x86_64.whl --no-deps
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
