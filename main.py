import json
import logging
import os
import subprocess
import sys

import ui

PYTHON_EXEC = 'python3.10'
PATH = os.path.dirname(os.path.abspath(__file__))
ROCM_VERSION = "6.1.2"

logger = logging.getLogger('ai-suite-rocm')
config = None


class Config:
    data = {}

    def __init__(self):
        self.file = os.path.join(os.path.expanduser("~"), ".config", "ai-suite-rocm", "config.json")

        self.create()
        self.read()

    def create(self):
        if not os.path.exists(self.file):
            os.makedirs(os.path.dirname(self.file), exist_ok=True)
            with open(self.file, "w") as f:
                f.write("{}")

            logger.info(f"Created config file at {self.file}")

    def read(self):
        with open(self.file, "r") as f:
            self.data = json.load(f)

    def write(self):
        with open(self.file, "w") as f:
            json.dump(self.data, f)

    def get(self, key: str):
        return self.data.get(key)

    def set(self, key: str, value):
        self.data[key] = value
        self.write()

    def has(self, key: str):
        return key in self.data

    def remove(self, key: str):
        self.data.pop(key)
        self.write()

    def clear(self):
        self.data = {}
        self.write()


def setup_logger(level: logger.level = logging.INFO):
    global logger
    if not logger.hasHandlers():
        logger.setLevel(level)
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter('[%(levelname)s] : %(message)s'))
        logger.addHandler(handler)


def setup_config():
    global config
    config = Config()


def get_config():
    global config
    return config


def run_command(command: str, exit_on_error: bool = True):
    logger.debug(f"Running command: {command}")
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = process.communicate()

    if process.returncode != 0:
        logger.fatal(f"Failed to run command: {command}")
        raise Exception(f"Failed to run command: {command}")

    return out, err, process.returncode


def check_for_build_essentials():
    logger.debug("Checking for build essentials...")
    debian = os.path.exists('/etc/debian_version')
    fedora = os.path.exists('/etc/fedora-release')

    if debian:
        # TODO: check if these work for debian users
        check_gcc = run_command("dpkg -l | grep build-essential &>/dev/null", exit_on_error=False)[2] == 0
        check_python = run_command("dpkg -l | grep python3.10-dev &>/dev/null", exit_on_error=False)[2] == 0

        if not check_gcc or not check_python:
            raise UserWarning(
                "The packages build-essential and python3.10-dev are required for this script to run. Please install them. See the README for more information.")
    elif fedora:
        check_gcc = run_command("rpm -q gcc &>/dev/null", exit_on_error=False)[2] == 0
        check_python = run_command("rpm -q python3.10-devel &>/dev/null", exit_on_error=False)[2] == 0

        if not check_gcc or not check_python:
            raise UserWarning(
                "The package python3.10-devel and the Development Tools group are required for this script to run. Please install them. See the README for more information.")
    else:
        logger.warning(
            "Unsupported OS detected. Please ensure you have the following packages installed or their equivalent: build-essential, python3.10-dev")


def run_interactive_cmd_ui():
    while True:
        choice = ui.start.ask()

        match choice:
            case "Start services":
                services = ui.start_services.ask()
                for service in services:
                    logger.info(f"Starting service: {service}")
                    pass
                pass
            case "Stop services":
                pass
            case "Install/update services":
                pass
            case "Uninstall services":
                pass
            case "Exit":
                print("Exiting...")
                exit(0)

if __name__ == '__main__':
    setup_logger(logging.DEBUG)
    setup_config()

    logger.info("Starting AI Suite for ROCM")
    check_for_build_essentials()

    run_interactive_cmd_ui()
