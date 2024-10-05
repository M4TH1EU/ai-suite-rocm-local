import importlib
import json
import os
import shutil
import subprocess
from pathlib import Path
from typing import List, Dict, Tuple, Union
from urllib import request, error

from core.stack import Stack
from core.vars import ROCM_VERSION, logger


def get_prebuilts(repo_owner: str = "M4TH1EU", repo_name: str = "ai-suite-rocm-local",
                  release_tag: str = f"prebuilt-whl-{ROCM_VERSION}") -> List[dict]:
    """
    Fetch prebuilt assets from a GitHub release using the GitHub API.

    :param repo_owner: GitHub repository owner
    :param repo_name: GitHub repository name
    :param release_tag: Release tag for fetching assets
    :return: List of assets (dictionaries) from the GitHub release
    """
    api_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/releases/tags/{release_tag}"

    try:
        with request.urlopen(api_url) as response:
            if response.status != 200:
                logger.error(f"Failed to fetch data: HTTP Status {response.status}")
                return []

            release_data = json.load(response)
            assets = release_data.get('assets', [])
            if not assets:
                logger.error("No assets found in release data")
                return []

            return assets

    except error.URLError as e:
        logger.error(f"Error fetching release data: {e}")
        return []


def check_for_build_essentials() -> None:
    """
    Check if build essentials like `build-essential` and `python3.10-dev` are installed.
    Raises a warning if they are missing.
    """
    logger.debug("Checking for build essentials...")
    debian = Path('/etc/debian_version').exists()
    fedora = Path('/etc/fedora-release').exists()

    if debian:
        check_gcc = run_command("dpkg -l | grep build-essential &>/dev/null", exit_on_error=False)[2] == 0
        check_python = run_command("dpkg -l | grep python3.10-dev &>/dev/null", exit_on_error=False)[2] == 0

        if not check_gcc or not check_python:
            raise UserWarning(
                "The packages build-essential and python3.10-dev are required for this script to run. Please install them. See the README for more information."
            )
    elif fedora:
        check_gcc = run_command("rpm -q gcc &>/dev/null", exit_on_error=False)[2] == 0
        check_python = run_command("rpm -q python3.10-devel &>/dev/null", exit_on_error=False)[2] == 0

        if not check_gcc or not check_python:
            raise UserWarning(
                "The package python3.10-devel and the Development Tools group are required for this script to run. Please install them. See the README for more information."
            )
    else:
        logger.warning(
            "Unsupported OS detected. Please ensure you have the following packages installed or their equivalent: build-essential, python3.10-dev"
        )


def run_command(command: str, exit_on_error: bool = True) -> Tuple[bytes, bytes, int]:
    """
    Run a shell command and return the output, error, and return code.

    :param command: The shell command to run
    :param exit_on_error: Whether to raise an exception on error
    :return: A tuple containing stdout, stderr, and return code
    """
    logger.debug(f"Running command: {command}")
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = process.communicate()

    if process.returncode != 0:
        logger.fatal(f"Failed to run command: {command}")

        if exit_on_error:
            raise Exception(f"Failed to run command: {command}")

    return out, err, process.returncode


def load_service_from_string(service: str) -> Stack:
    """
    Dynamically load a Stack class based on the service string.

    :param service: Name of the service to load
    :return: An instance of the corresponding Stack class
    """
    logger.debug(f"Loading service from string: {service}")

    service_name = service.replace("_", " ").title().replace(" ", "")
    module = importlib.import_module(f"services.{service}")
    stack_class = getattr(module, service_name)

    return stack_class()


def find_symlink_in_folder(folder: Union[str, Path]) -> Dict[Path, Path]:
    """
    Find all symbolic links in the given folder and map them to their resolved paths.

    :param folder: The folder to search for symlinks
    :return: A dictionary mapping symlink paths to their resolved target paths
    """
    folder = Path(folder)
    symlinks = {}

    for file in folder.rglob("webui/**"):
        if file.is_symlink():
            symlinks[file] = file.resolve()

    return symlinks


def create_symlinks(symlinks: Dict[Path, Path]) -> None:
    """
    Recreate symlinks from a dictionary mapping target paths to link paths.

    :param symlinks: Dictionary of symlinks and their resolved paths
    """
    for target, link in symlinks.items():
        logger.debug(f"(re)Creating symlink: {link} -> {target}")

        if target.is_symlink():
            target.unlink()

        if target.exists() and target.is_dir():
            shutil.rmtree(target)

        os.symlink(link, target)
