from services import Stack


class StableDiffusionForge(Stack):
    def __init__(self):
        super().__init__(
            'StableDiffusion Forge WebUI',
            'stablediffusion-forge-rocm',
            5003,
            'https://github.com/lllyasviel/stable-diffusion-webui-forge'
        )

    def install(self):
        # Install the webui
        self.git_clone(url=self.url, dest="webui")

        self.python("launch.py --skip-torch-cuda-test --exit", current_dir="webui")

        # Add NF4 support for Flux
        self.install_from_prebuilt("bitsandbytes")

        super().install()

    def start(self):
        args = ["--listen", "--enable-insecure-extension-access", "--port", str(self.port)]
        self.python(f"launch.py {' '.join(args)}", current_dir="webui",
                    env=["TORCH_BLAS_PREFER_HIPBLASLT=0"])
