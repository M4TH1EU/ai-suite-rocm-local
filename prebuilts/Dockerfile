FROM rocm/dev-ubuntu-22.04:6.1.2

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PYTHONIOENCODING=UTF-8 \

    # for bitsandbytes
    ROCM_ARCH="gfx1030" \
    TORCH_VERSION="rocm6.1" \

    # for llama
    CMAKE_ARGS="-DGGML_HIPBLAS=on" \
    FORCE_CMAKE=1


WORKDIR /tmp

RUN apt-get update -y
RUN apt-get install -y wget git cron cmake make software-properties-common

# Install python3.10
RUN add-apt-repository ppa:deadsnakes/ppa -y && apt-get update -y
RUN apt-get install -y python3.10 python3.10-dev python3.10-venv

ENV VIRTUAL_ENV=/opt/venv
RUN python3.10 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN pip3 install --upgrade pip wheel setuptools build

# Install pytorch for rocm
RUN pip3 install --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/${TORCH_VERSION}


# ROCM bitsandbytes
RUN apt-get install -y hipblas hipblaslt hiprand hipsparse hipcub rocthrust-dev
## Clone repo and install python requirements
RUN git clone --depth 1 -b multi-backend-refactor https://github.com/bitsandbytes-foundation/bitsandbytes.git
WORKDIR /tmp/bitsandbytes
RUN pip3 install -r requirements-dev.txt
## Build
RUN cmake -DCOMPUTE_BACKEND=hip -S . -DBNB_ROCM_ARCH=${ROCM_ARCH}
RUN make
RUN python3.10 setup.py bdist_wheel --universal


# ROCM llama-cpp-python
RUN apt-get install -y hipblas hipblaslt hiprand hipsparse hipcub rocthrust-dev
## Clone repo and install python requirements
RUN git clone --recurse-submodules https://github.com/abetlen/llama-cpp-python.git
WORKDIR /tmp/llama-cpp-python
RUN python3.10 -m build --wheel


# Cleanup
RUN apt-get clean && pip3 cache purge
