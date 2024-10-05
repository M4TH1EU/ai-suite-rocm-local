from pathlib import Path

from core.stack import Stack


class TextGenerationWebui(Stack):

    def __init__(self):
        super().__init__(
            'Text Generation',
            'text_generation_webui',
            5000,
            'https://github.com/oobabooga/text-generation-webui/'
        )

        self.exllama = "0.2.1"

    def _install(self):
        # Install LlamaCpp from prebuilt
        self.pip_install("llama-cpp-python", env=["CMAKE_ARGS=\"-DGGML_BLAS=ON -DGGML_BLAS_VENDOR=OpenBLAS\""])  # cpu

        # Install LlamaCpp for ROCM from source
        # self.pip_install("llama-cpp-python", env=["CMAKE_ARGS=\"-DGGML_HIPBLAS=on\" FORCE_CMAKE=1"]) # manual gpu (only works if whole rocm suite installed)
        # self.install_from_prebuilt("llama_cpp_python") # gpu (only works if whole rocm suite installed)

        # Install Triton for ROCM from prebuilt
        # self.install_from_prebuilt("triton")

        # Install Triton for ROCM from source
        # self.git_clone(url="https://github.com/ROCmSoftwarePlatform/triton.git")
        # self.pip_install(['ninja', 'cmake'])
        # self.pip("install -e .", path="triton")

        # Install the webui
        self.git_clone(url=self.url, dest=Path(self.path / "webui"))
        self.remove_line_in_file(["accelerate", "lm_eval", "optimum", "autoawq", "llama_cpp_python"],
                                 "webui/requirements_amd.txt")
        self.install_requirements("webui/requirements_amd.txt")
        self.pip_install(["accelerate", "optimum"])
        self.pip_install(
            "https://github.com/casper-hansen/AutoAWQ_kernels/releases/download/v0.0.7/autoawq_kernels-0.0.7+rocm571-cp310-cp310-linux_x86_64.whl",
            no_deps=True)
        self.pip_install(
            "https://github.com/casper-hansen/AutoAWQ/releases/download/v0.2.6/autoawq-0.2.6-cp310-cp310-linux_x86_64.whl",
            no_deps=True)
        # Fix llama trying to use cuda version
        self.remove_line_in_file("llama_cpp_cuda", "webui/modules/llama_cpp_python_hijack.py")

        # Install ExLlamaV2 and auto-gptq
        self.pip_install(
            f"https://github.com/turboderp/exllamav2/releases/download/v{self.exllama}/exllamav2-{self.exllama}+rocm6.1.torch2.4.0-cp310-cp310-linux_x86_64.whl")
        self.install_from_prebuilt("bitsandbytes")
        self.pip_install("auto-gptq", args=["--no-build-isolation", "--extra-index-url",
                                            "https://huggingface.github.io/autogptq-index/whl/rocm573/"])

    def _update(self):
        self.pip_install(
            f"https://github.com/turboderp/exllamav2/releases/download/v{self.exllama}/exllamav2-{self.exllama}+rocm6.1.torch2.4.0-cp310-cp310-linux_x86_64.whl")
        self.pip_install("auto-gptq", args=["--no-build-isolation", "--extra-index-url",
                                            "https://huggingface.github.io/autogptq-index/whl/rocm573/"])

    def _start(self):
        args = ["--listen", "--listen-port", str(self.port)]
        self.python(f"server.py", args=args, current_dir=Path(self.path / "webui"),
                    env=["TORCH_BLAS_PREFER_HIPBLASLT=0"], daemon=True)
