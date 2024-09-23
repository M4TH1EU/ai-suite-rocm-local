ARG ROCM_VERSION=6.2
FROM rocm/dev-ubuntu-22.04:${ROCM_VERSION}
# also works without -complete for specific arch (tested on gfx1030)

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PYTHONIOENCODING=UTF-8

# For bitsandbytes
ENV BNB_GPU_TARGETS="gfx803;gfx900;gfx906;gfx908;gfx90a;gfx1010;gfx1030;gfx1100;gfx1101;gfx1102"
# For LLAMA
# Synthax error but works
ARG ROCM_DOCKER_ARCH=\
    gfx803 \
    gfx900 \
    gfx906 \
    gfx908 \
    gfx90a \
    gfx1010 \
    gfx1030 \
    gfx1100 \
    gfx1101 \
    gfx1102
# no synthax error but doesn't work for some reason (error on llama compile)??
# CMake Error: The source directory "/tmp/llama-cpp-python/gfx1102" does not exist.
# ARG ROCM_DOCKER_ARCH="gfx803 gfx 900 gfx906 gfx908 gfx90a gfx1010 gfx1030 gfx1100 gfx1101 gfx1102"

ENV GPU_TARGETS=${ROCM_DOCKER_ARCH}

ENV CC=/opt/rocm/llvm/bin/clang
ENV CXX=/opt/rocm/llvm/bin/clang++

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
# Install deps
RUN apt-get install -y hipblas hipblaslt hiprand hipsparse hipcub rocthrust-dev

COPY entrypoint.sh /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]

# Cleanup
RUN apt-get clean && pip3 cache purge
