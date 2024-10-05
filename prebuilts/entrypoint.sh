#!/bin/sh -l

# ROCM bitsandbytes
## Clone repo and install python requirements
git clone --depth 1 -b multi-backend-refactor https://github.com/bitsandbytes-foundation/bitsandbytes.git /tmp/bitsandbytes
cd /tmp/bitsandbytes
pip3 install -r requirements-dev.txt
## Build
cmake -DCOMPUTE_BACKEND=hip -S . -DBNB_ROCM_ARCH=${BNB_GPU_TARGETS}
make
python3.10 setup.py bdist_wheel --universal


# ROCM llama-cpp-python
## Clone repo and install python requirements
git clone --recurse-submodules https://github.com/abetlen/llama-cpp-python.git /tmp/llama-cpp-python
cd /tmp/llama-cpp-python
CMAKE_ARGS="-D GGML_HIPBLAS=on -D AMDGPU_TARGETS=${GPU_TARGETS}" FORCE_CMAKE=1 python3.10 -m build --wheel


# ROCM xformers
## Clone repo and install python requirements
pip3 install ninja
git clone --depth 1 https://github.com/facebookresearch/xformers.git /tmp/xformers
cd /tmp/xformers
python3.10 setup.py bdist_wheel --universal