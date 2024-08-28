from services import Stack


class BGRemovalDIS(Stack):
    def __init__(self):
        super().__init__(
            'BGRemovalDIS',
            'bg-remove-dis-rocm',
            5005,
            'https://huggingface.co/spaces/ECCV2022/dis-background-removal'
        )

    def install(self):
        self.git_clone(url=self.url, dest="webui")
        self.install_requirements("webui/requirements.txt")
        self.pip_install("gradio")  # gradio is not in requirements.txt for some reason

        self.remove_line_in_file("os.", "webui/app.py")  # remove manual clone of DIS from app.py (done below)

        self.git_clone("https://github.com/xuebinqin/DIS.git", dest="tmp-dis")
        self.move_all_files_in_dir("tmp-dis/IS-Net", "webui")
        self.remove_dir("tmp-dis")

        self.create_dir("webui/saved_models")
        self.move_file_or_dir("webui/isnet.pth", "webui/saved_models/isnet.pth")

        # self.remove_dir("webui/.git") # saves a lot of space due to big repo

        super().install()

    def start(self):
        args = ["--port", str(self.port)]
        self.python(f"app.py {' '.join(args)}", current_dir="webui",
                    env=["TORCH_BLAS_PREFER_HIPBLASLT=0"])
