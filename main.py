import logging
import sys

from core import config
from core.utils import check_for_build_essentials, load_service_from_string
from core.vars import logger, services, loaded_services
from ui.choices import update_choices
from ui.interface import run_interactive_cmd_ui


def setup_logger(level: logger.level = logging.INFO):
    if not logger.hasHandlers():
        logger.setLevel(level)
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter('[%(levelname)s] : %(message)s'))
        logger.addHandler(handler)


def setup_config():
    config.create()
    config.read()


def load_services():
    for service in services:
        loaded_services[service] = load_service_from_string(service)


if __name__ == '__main__':
    setup_logger(logging.INFO)
    logger.info("Starting AI Suite for ROCM")

    setup_config()

    check_for_build_essentials()

    load_services()

    update_choices()
    run_interactive_cmd_ui()
