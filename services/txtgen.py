from services import Stack


class TextGeneration(Stack):
    def __init__(self):
        super().__init__(
            'Text Generation',
            'text-generation-rocm',
            5000,
            'https://github.com/oobabooga/text-generation-webui/'
        )

    def install(self):
        # Install LlamaCpp from prebuilt
        self.pip("install llama-cpp-python", ["CMAKE_ARGS=\"-DGGML_BLAS=ON -DGGML_BLAS_VENDOR=OpenBLAS\""])  # cpu

        # Install LlamaCpp for ROCM from source
        # self.pip("install llama-cpp-python", ["CMAKE_ARGS=\"-DGGML_HIPBLAS=on\" FORCE_CMAKE=1"]) # manual gpu (only works if whole rocm suite installed)
        # self.install_from_prebuilt("llama_cpp_python") # gpu (only works if whole rocm suite installed)

        # Install Triton for ROCM from prebuilt
        # self.install_from_prebuilt("triton")

        # Install Triton for ROCM from source
        # self.git_clone(url="https://github.com/ROCmSoftwarePlatform/triton.git")
        # self.pip_install(['ninja', 'cmake'])
        # self.pip("install -e .", path="triton")

        # Install the webui
        self.git_clone(url=self.url, dest="webui")
        self.remove_line_in_file(["accelerate", "lm_eval", "optimum", "autoawq", "llama_cpp_python"],
                                 "../text-generation-rocm/webui/requirements_amd.txt")
        self.install_requirements("../text-generation-rocm/webui/requirements_amd.txt")
        self.pip_install(["accelerate", "optimum"])
        self.pip_install(
            "https://github.com/casper-hansen/AutoAWQ_kernels/releases/download/v0.0.7/autoawq_kernels-0.0.7+rocm571-cp310-cp310-linux_x86_64.whl",
            no_deps=True)
        self.pip_install(
            "https://github.com/casper-hansen/AutoAWQ/releases/download/v0.2.6/autoawq-0.2.6-cp310-cp310-linux_x86_64.whl",
            no_deps=True)
        # Fix llama trying to use cuda version
        self.remove_line_in_file("llama_cpp_cuda", "../text-generation-rocm/webui/modules/llama_cpp_python_hijack.py")

        # Install useful packages
        self.pip_install(
            "https://github.com/turboderp/exllamav2/releases/download/v0.1.9/exllamav2-0.1.9+rocm6.1.torch2.4.0-cp310-cp310-linux_x86_64.whl")
        self.install_from_prebuilt("bitsandbytes")
        self.pip(
            "install auto-gptq --no-build-isolation --extra-index-url https://huggingface.github.io/autogptq-index/whl/rocm573/")

        super().install()

    def start(self):
        args = ["--listen", "--listen-port", str(self.port)]
        self.python(f"server.py {' '.join(args)}", current_dir="webui",
                    env=["TORCH_BLAS_PREFER_HIPBLASLT=0"])
