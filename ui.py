import questionary
from questionary import Choice

from services import BGRemovalDIS, ComfyUI, StableDiffusionWebUI, StableDiffusionForge, TextGeneration, XTTS

services = {
    "Background Removal (DIS)": BGRemovalDIS,
    "ComfyUI": ComfyUI,
    "StableDiffusion (AUTOMATIC1111)": StableDiffusionWebUI,
    "StableDiffusion Forge": StableDiffusionForge,
    "TextGeneration (oobabooga)": TextGeneration,
    "XTTS": XTTS
}

start = questionary.select(
    "Choose an option:",
    choices=[
        Choice("Start services"),
        Choice("Stop services"),
        Choice("Install/update services"),
        Choice("Uninstall services"),
        Choice("Exit")
    ])

start_services = questionary.checkbox(
    "Select services to start:",
    choices=[Choice(service) for service in services.keys()]
)

stop_services = questionary.checkbox(
    "Select services to stop:",
    choices=[Choice(service) for service in services.keys()]
)

install_service = questionary.checkbox(
    "Select service to install/update:",
    choices=[Choice(service) for service in services.keys()]
)

uninstall_service = questionary.checkbox(
    "Select service to uninstall:",
    choices=[Choice(service) for service in services.keys()]
)
