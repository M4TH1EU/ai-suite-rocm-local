#!/bin/sh -l

# ROCM bitsandbytes
## Clone repo and install python requirements
git clone --depth 1 -b multi-backend-refactor https://github.com/bitsandbytes-foundation/bitsandbytes.git
cd /tmp/bitsandbytes
pip3 install -r requirements-dev.txt
## Build
cmake -DCOMPUTE_BACKEND=hip -S . -DBNB_ROCM_ARCH=${ROCM_ARCH}
make
python3.10 setup.py bdist_wheel --universal


# ROCM llama-cpp-python
## Clone repo and install python requirements
git clone --recurse-submodules https://github.com/abetlen/llama-cpp-python.git
cd /tmp/llama-cpp-python
CMAKE_ARGS="-DGGML_HIPBLAS=on" python3.10 -m build --wheel