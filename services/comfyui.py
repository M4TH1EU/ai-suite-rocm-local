from services import Stack


class ComfyUI(Stack):
    def __init__(self):
        super().__init__(
            'ComfyUI',
            'comfyui-rocm',
            5004,
            'https://github.com/comfyanonymous/ComfyUI.git'
        )

    def install(self):
        # Install the webui
        self.git_clone(url=self.url, dest="webui")
        self.install_requirements("webui/requirements.txt")

        # Install the manager
        self.git_clone(url="https://github.com/ltdrdata/ComfyUI-Manager.git", dest="webui/custom_nodes/manager")

        # Add GGUF support
        self.pip_install(["gguf", "numpy==1.26.4"])

        # Add NF4 support for Flux
        self.install_from_prebuilt("bitsandbytes")
        self.git_clone(url="https://github.com/comfyanonymous/ComfyUI_bitsandbytes_NF4.git",
                       dest="webui/custom_nodes/ComfyUI_bitsandbytes_NF4")

        super().install()

    def _launch(self):
        args = ["--port", str(self.port)]
        self.python(f"main.py {' '.join(args)}", current_dir="webui",
                    env=["TORCH_BLAS_PREFER_HIPBLASLT=0"])
