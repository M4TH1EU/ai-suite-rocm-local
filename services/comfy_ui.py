from core.stack import Stack


class ComfyUi(Stack):
    def __init__(self):
        super().__init__(
            'ComfyUI',
            'comfy_ui',
            5004,
            'https://github.com/comfyanonymous/ComfyUI.git'
        )

    def _install(self):
        # Install the webui
        self.git_clone(url=self.url, dest="webui")
        self.install_requirements("webui/requirements.txt")

        # Install the manager
        self.git_clone(url="https://github.com/ltdrdata/ComfyUI-Manager.git", dest="webui/custom_nodes/manager")

        # Add GGUF support
        self.git_clone(url="https://github.com/city96/ComfyUI-GGUF.git", dest="webui/custom_nodes/ComfyUI-GGUF")
        self.pip_install(["gguf", "numpy==1.26.4"])

        # Add NF4 support for Flux
        self.install_from_prebuilt("bitsandbytes")
        self.git_clone(url="https://github.com/comfyanonymous/ComfyUI_bitsandbytes_NF4.git",
                       dest="webui/custom_nodes/ComfyUI_bitsandbytes_NF4")

    def _start(self):
        args = ["--port", str(self.port), "--force-fp32"]
        self.python(f"main.py", args=args, current_dir="webui",
                    env=["TORCH_BLAS_PREFER_HIPBLASLT=0"], daemon=True)
