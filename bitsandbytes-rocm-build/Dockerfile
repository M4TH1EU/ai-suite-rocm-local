FROM rocm/dev-ubuntu-22.04:6.1.2

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PYTHONIOENCODING=UTF-8 \
    ROCM_ARCH="gfx1030"

WORKDIR /tmp

RUN apt-get update -y
RUN apt-get install -y wget git cron cmake make

# Install python3
RUN apt-get install -y python3 python3-dev
RUN curl -sS https://bootstrap.pypa.io/get-pip.py | python3
RUN pip3 install --upgrade pip wheel setuptools
# Install pytorch for rocm
RUN pip3 install --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/rocm6.1

# ROCM bitsandbytes
RUN apt-get install -y hipblas hipblaslt hiprand hipsparse hipcub rocthrust-dev
## Clone repo and install python requirements
RUN git clone --recurse https://github.com/ROCm/bitsandbytes
WORKDIR /tmp/bitsandbytes
RUN git checkout rocm_enabled
RUN pip3 install -r requirements-dev.txt
## Build
RUN cmake -DCOMPUTE_BACKEND=hip -S . -DBNB_ROCM_ARCH=${ROCM_ARCH}
RUN make

# Cleanup
RUN apt-get clean && pip3 cache purge