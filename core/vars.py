import logging
import os

PYTHON_EXEC = 'python3.10'
PATH = os.path.dirname(os.path.abspath(__file__))
ROCM_VERSION = "6.2"

logger = logging.getLogger('ai-suite-rocm')

services = [
    'background_removal_dis',
    'comfy_ui',
    'stable_diffusion_webui',
    'stable_diffusion_forge',
    'text_generation_webui',
    'xtts_webui'
]

loaded_services = {}
