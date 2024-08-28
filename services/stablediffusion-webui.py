from services import Stack


class StableDiffusionForge(Stack):
    def __init__(self):
        super().__init__(
            'StableDiffusion WebUI',
            'stablediffusion-webui-rocm',
            5002,
            'https://github.com/AUTOMATIC1111/stable-diffusion-webui'
        )

    def install(self):
        # Install the webui
        self.git_clone(url=self.url, branch="dev", dest="webui")

        self.python("launch.py --skip-torch-cuda-test --exit", current_dir="webui")

        # Add NF4 support for Flux
        self.install_from_prebuilt("bitsandbytes")

        super().install()

    def start(self):
        args = ["--listen", "--enable-insecure-extension-access", "--port", str(self.port)]
        self.python(f"launch.py {' '.join(args)}", current_dir="webui",
                    env=["TORCH_BLAS_PREFER_HIPBLASLT=0"])
