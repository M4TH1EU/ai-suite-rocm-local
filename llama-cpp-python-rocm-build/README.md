# llama-cpp-python-rocm-build-pip

This is a simple script to help you build the latest llama-cpp-python for rocm.
The official build process requires a lot of ROCM-related packages and can mess up your computer easily if you install the wrong packages.

This creates a Docker image that builds the package and extract the built wheel file that you can then easily install using pip.

```bash
./build.sh
./extract_build.sh
```

The wheel file will be in a folder named ``build_output/``

*You might also find one of my already built wheel in this folder or on the github releases page (may not be up to date)*

