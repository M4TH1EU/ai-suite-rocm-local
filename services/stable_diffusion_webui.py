from core.stack import Stack


class StableDiffusionWebui(Stack):
    def __init__(self):
        super().__init__(
            'StableDiffusion WebUI',
            'stable_diffusion_webui',
            5002,
            'https://github.com/AUTOMATIC1111/stable-diffusion-webui'
        )

    def _install(self):
        # Install the webui
        self.git_clone(url=self.url, branch="dev", dest="webui")

        self.python("launch.py --skip-torch-cuda-test --exit", current_dir="webui")

        # Add NF4 support for Flux
        self.install_from_prebuilt("bitsandbytes")

    def _start(self):
        args = ["--listen", "--enable-insecure-extension-access", "--port", str(self.port)]
        self.python(f"launch.py", args=args, current_dir="webui",
                    env=["TORCH_BLAS_PREFER_HIPBLASLT=0"], daemon=True)
