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
        $python_exec -m pip install --upgrade https://github.com/M4TH1EU/ai-suite-rocm-local/releases/download/prebuilt-wheels-for-rocm/bitsandbytes-0.43.3-cp310-cp310-linux_x86_64.whl # install bitsandbytes for rocm until it is available on pypi

        # Add AutoGPTQ
        $python_exec -m pip install auto-gptq --no-build-isolation --extra-index-url https://huggingface.github.io/autogptq-index/whl/rocm573/

        # Add ExLlamav2
        $python_exec -m pip install https://github.com/turboderp/exllamav2/releases/download/v0.1.9/exllamav2-0.1.9+rocm6.1.torch2.4.0-cp310-cp310-linux_x86_64.whl

        # Add LlamaCPP
        CMAKE_ARGS="-DGGML_BLAS=ON -DGGML_BLAS_VENDOR=OpenBLAS" pip install llama-cpp-python # cpu
        # CMAKE_ARGS="-DGGML_HIPBLAS=on" FORCE_CMAKE=1 $python_exec -m pip install llama-cpp-python # gpu

        # llama cpp built with hipblas doesn't work unless the whole rocm stack is installed locally
        # so for now, use llama with openblas (cpu)

#        main_venv_path=$(dirname $(python -c "import torch; print(torch.__file__)"))"/lib/"
#        llama_lib_path="$(pwd)/venv/lib64/python3.10/site-packages/llama_cpp/lib"
#
#        for file in "$main_venv_path"/*.so; do
#            ln -s "$file" "$llama_lib_path/$(basename "$file")"
#        done

#        ln -s "$llama_lib_path/libhipblas.so" "$llama_lib_path/libhipblas.so.1"
#        ln -s "$llama_lib_path/libhipblas.so" "$llama_lib_path/libhipblas.so.2"
#        ln -s "$llama_lib_path/librocblas.so" "$llama_lib_path/librocblas.so.3"
#        ln -s "$llama_lib_path/librocblas.so" "$llama_lib_path/librocblas.so.4"
#        ln -s "$llama_lib_path/libamdhip64.so" "$llama_lib_path/libamdhip64.so.5"
#        ln -s "$llama_lib_path/libamdhip64.so" "$llama_lib_path/libamdhip64.so.6"


        # Add Triton
#        $python_exec -m pip install https://github.com/M4TH1EU/ai-suite-rocm-local/releases/download/prebuilt-wheels-for-rocm/llama_cpp_python-0.2.89-cp310-cp310-linux_x86_64.whl
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
        sed -i '/llama_cpp_python/d' webui/requirements_amd.txt

        $python_exec -m pip install -r webui/requirements_amd.txt

        # only works after requirements_amd.txt is installed ??!
        $python_exec -m pip install accelerate optimum
        $python_exec -m pip install https://github.com/casper-hansen/AutoAWQ_kernels/releases/download/v0.0.7/autoawq_kernels-0.0.7+rocm571-cp310-cp310-linux_x86_64.whl --no-deps
        $python_exec -m pip install https://github.com/casper-hansen/AutoAWQ/releases/download/v0.2.6/autoawq-0.2.6-cp310-cp310-linux_x86_64.whl --no-deps
        $python_exec -m pip install lm_eval
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
