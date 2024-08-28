from services import Stack


class XTTS(Stack):
    def __init__(self):
        super().__init__(
            'XTTS WebUI',
            'xtts-rocm',
            5001,
            'https://github.com/daswer123/xtts-webui'
        )

    def install(self):
        # Install the webui
        self.git_clone(url=self.url, dest="webui")

        self.remove_line_in_file("torch", "webui/requirements.txt")
        self.install_requirements("webui/requirements.txt")

        #     sed -i 's/device = "cuda" if torch.cuda.is_available() else "cpu"/device = "cpu"/' webui/scripts/utils/formatter.py
        #     sed -i 's/asr_model = WhisperModel(whisper_model, device=device, compute_type="float16")/asr_model = WhisperModel(whisper_model, device=device, compute_type="int8")/' webui/scripts/utils/formatter.py

        # Disable gpu for faster-whipser as ROCM isn't supported yet
        self.replace_line_in_file("device = \"cuda\" if torch.cuda.is_available() else \"cpu\"", "device = \"cpu\"",
                                  "webui/scripts/utils/formatter.py")
        self.replace_line_in_file("asr_model = WhisperModel(whisper_model, device=device, compute_type=\"float16\")",
                                  "asr_model = WhisperModel(whisper_model, device=device, compute_type=\"int8\")",
                                  "webui/scripts/utils/formatter.py")

        # Deepspeed and ninja (not working yet)
        # self.pip_install(["ninja", "deepspeed"])

        super().install()

    def _launch(self):
        args = ["--host", "0.0.0.0", "--port", str(self.port)]
        self.python(f"server.py {' '.join(args)}", current_dir="webui",
                    env=["TORCH_BLAS_PREFER_HIPBLASLT=0"])
