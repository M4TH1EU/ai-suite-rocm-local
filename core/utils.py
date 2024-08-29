import importlib
import json
import os
import subprocess
import urllib

from core.stack import Stack
from core.vars import ROCM_VERSION, logger


def get_prebuilts(repo_owner: str = "M4TH1EU", repo_name: str = "ai-suite-rocm-local",
                  release_tag: str = f"prebuilt-whl-{ROCM_VERSION}") -> list:
    api_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/releases/tags/{release_tag}"

    try:
        with urllib.request.urlopen(api_url) as response:
            if response.status != 200:
                logger.error(f"Failed to fetch data: HTTP Status {response.status}")
                return []

            release_data = json.load(response)

            assets = release_data.get('assets', [])
            if not assets:
                logger.error("No assets found in release data")
                return []

            return assets

    except urllib.error.URLError as e:
        logger.error(f"Error fetching release data: {e}")


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


def run_command(command: str, exit_on_error: bool = True):
    logger.debug(f"Running command: {command}")
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = process.communicate()

    if process.returncode != 0:
        logger.fatal(f"Failed to run command: {command}")

        if exit_on_error:
            raise Exception(f"Failed to run command: {command}")

    return out, err, process.returncode


def load_service_from_string(service: str) -> Stack:
    logger.debug(f"Loading service from string: {service}")

    service_name = service.replace("_", " ").title().replace(" ", "")

    module = importlib.import_module(f"services.{service}")
    met = getattr(module, service_name)
    return met()

