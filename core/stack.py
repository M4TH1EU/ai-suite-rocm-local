import os
import shutil
import subprocess
from pathlib import Path
from typing import Union, List, Optional

import psutil

from core import utils, screen
from core.screen import Screen
from core.vars import logger, PYTHON_EXEC
from ui import choices


class Stack:
    def __init__(self, name: str, id: str, port: int, url: str):
        """
        Initialize the Stack instance.

        :param name: The name of the stack
        :param id: A unique identifier for the stack
        :param port: The port the stack service uses
        :param url: The URL associated with the stack
        """
        self.name = name
        self.id = id
        self.path = Path.home() / ".ai-suite-rocm" / id
        self.url = url
        self.port = port
        self.pid_file = self.path / f".pid"
        self.pid = self.read_pid()
        self.screen_session: Screen = None

    def read_pid(self) -> Optional[int]:
        """
        Read the PID from the PID file, if it exists.

        :return: The PID as an integer, or None if the file does not exist or an error occurs.
        """
        if self.pid_file.exists():
            return int(self.pid_file.read_text())
        else:
            return None

    def write_pid(self, pid: int) -> None:
        """
        Write the PID to the PID file.

        :param pid: Process ID to write
        """
        with self.pid_file.open('w') as f:
            f.write(str(pid))

    def remove_pid_file(self) -> None:
        """Remove the PID file if it exists."""
        if self.pid_file.exists():
            self.pid_file.unlink()

    def install(self) -> None:
        """Install the stack, creating the virtual environment and performing initial setup."""
        if self.is_installed():
            self.update()
        else:
            self.check_for_broken_install()
            self.create_dir('')
            self.create_venv()
            self._install()

            self.create_file('.installed', 'true')
            logger.info(f"Installed {self.name}")

    def _install(self) -> None:
        """Additional installation steps specific to the stack (override as needed)."""
        pass

    def is_installed(self) -> bool:
        """
        Check if the stack is installed by verifying the existence of the '.installed' file.

        :return: True if the stack is installed, False otherwise.
        """
        return self.file_exists('.installed')

    def check_for_broken_install(self) -> None:
        """Check for a broken installation and clean up any leftover files."""
        if not self.is_installed() and self.path.exists():
            logger.warning("Found files from a previous/broken/crashed installation, cleaning up...")
            self.remove_dir('')

    def update(self, folder: str = 'webui') -> None:
        """Update the stack by pulling the latest changes from the repository."""
        if self.is_installed():
            was_running = self.status()
            if was_running:
                self.stop()

            logger.info(f"Updating {self.name}")
            symlinks = utils.find_symlink_in_folder(self.path)
            self.git_pull(folder)
            self._update()
            utils.create_symlinks(symlinks)

            if was_running:
                self.start()
        else:
            logger.warning(f"Could not update {self.name} as {self.name} is not installed")

    def _update(self) -> None:
        """Additional update steps specific to the stack (override as needed)."""
        pass

    def uninstall(self) -> None:
        """Uninstall the stack by stopping it and removing its files."""
        logger.info(f"Uninstalling {self.name}")
        if self.status():
            self.stop()
        self.bash(f"rm -rf {self.path}")
        self.remove_pid_file()

    def start(self) -> None:
        """Start the stack service."""
        if self.status():
            logger.warning(f"{self.name} is already running")
            return

        if self.is_installed():
            self._start()
        else:
            logger.error(f"{self.name} is not installed")

    def _start(self) -> None:
        """Additional start steps specific to the stack (override as needed)."""
        pass

    def stop(self) -> None:
        """Stop the stack service by terminating the associated process."""
        if self.status():
            logger.debug(f"Stopping {self.name} with PID: {self.pid}")
            try:
                proc = psutil.Process(self.pid)
                proc.terminate()  # Graceful shutdown
                proc.wait(timeout=5)
            except (psutil.NoSuchProcess, psutil.TimeoutExpired):
                logger.warning(f"{self.name} did not terminate gracefully, forcing kill")
                psutil.Process(self.pid).kill()
            self.remove_pid_file()
        else:
            logger.warning(f"{self.name} is not running")

    def restart(self) -> None:
        """Restart the stack service."""
        self.stop()
        self.start()

    def status(self) -> bool:
        """
        Check if the stack service is running.

        :return: True if the service is running, False otherwise.
        """
        if self.screen_session and self.pid:
            return screen.exists(self.screen_session.pid)
        else:
            return self.pid is not None and psutil.pid_exists(self.pid)

    def create_venv(self) -> None:
        """Create a Python virtual environment for the stack."""
        venv_path = self.path / 'venv'
        if not self.has_venv():
            logger.info(f"Creating venv for {self.name}")
            self.bash(f"{PYTHON_EXEC} -m venv {venv_path} --system-site-packages")
            self.pip_install("pip")
        else:
            logger.debug(f"Venv already exists for {self.name}")

    def has_venv(self) -> bool:
        """
        Check if the virtual environment exists.

        :return: True if the virtual environment exists, False otherwise.
        """
        return (self.path / 'venv').exists()

    def pip_install(self, package: Union[str, List[str]], no_deps: bool = False, env: List[str] = [],
                    args: List[str] = []) -> None:
        """Install a Python package or list of packages using pip."""
        if no_deps:
            args.append("--no-deps")

        if isinstance(package, list):
            for p in package:
                logger.info(f"Installing {p}")
                self.pip(f"install -U {p}", env=env, args=args)
        else:
            logger.info(f"Installing {package}")
            self.pip(f"install -U {package}", env=env, args=args)

    def install_requirements(self, filename: str = 'requirements.txt', env: List[str] = []) -> None:
        """Install requirements from a given file."""
        logger.info(f"Installing requirements for {self.name} ({filename})")
        self.pip(f"install -r {filename}", env=env)

    def pip(self, cmd: str, env: List[str] = [], args: List[str] = [], current_dir: Optional[Path] = None) -> None:
        """Run pip with a given command."""
        self.python(f"-m pip {cmd}", env=env, args=args, current_dir=current_dir)

    def python(self, cmd: str, env: List[str] = [], args: List[str] = [], current_dir: Optional[Path] = None,
               daemon: bool = False) -> None:
        """Run a Python command inside the stack's virtual environment."""
        self.bash(f"{' '.join(env)} {self.path / 'venv' / 'bin' / 'python'} {cmd} {' '.join(args)}", current_dir,
                  daemon)

    def bash(self, cmd: str, current_dir: Optional[Path] = None, daemon: bool = False) -> None:
        """Run a bash command, optionally as a daemon."""
        full_cmd = f"cd {current_dir or self.path} && {cmd}"

        if daemon:
            if self.status():
                choice = choices.already_running.ask()
                if choice is True:
                    self.stop()
                    self._start()
                    return
                else:
                    return
            else:
                logger.debug(f"Running command as daemon: {full_cmd}")

                # process = subprocess.Popen(full_cmd, shell=True, preexec_fn=os.setpgrp,
                #                            stdout=config.open_file(f"{self.id}-stdout"),
                #                            stderr=config.open_file(f"{self.id}-stderr"))
                self.screen_session = screen.create(name=self.id)
                self.screen_session.send(f"'{full_cmd} && screen -wipe'")
                self.write_pid(self.screen_session.pid)
                return
        else:
            logger.debug(f"Running command: {full_cmd}")

            process = subprocess.Popen(full_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = process.communicate()

            if process.returncode != 0:
                logger.fatal(f"Failed to run command: {full_cmd}")
                logger.fatal(f"Error: {err.decode('utf-8')}")
                logger.fatal(f"Output: {out.decode('utf-8')}")
                raise Exception(f"Failed to run command: {full_cmd}")

    def git_clone(self, url: str, branch: Optional[str] = None, dest: Optional[Path] = None) -> None:
        """Clone a git repository."""
        logger.info(f"Cloning {url}")
        self.bash(f"git clone {f'-b {branch}' if branch else ''} {url} {dest or ''}")

    def git_pull(self, repo_folder: str, force: bool = False) -> None:
        """Pull changes from a git repository."""
        self.bash(f"git reset --hard HEAD {'&& git clean -f -d' if force else ''} && git pull", Path(repo_folder))

    def install_from_prebuilt(self, name):
        for prebuilt in utils.get_prebuilts():
            if prebuilt['name'].split("-")[0] == name:
                self.pip(f"install {prebuilt['browser_download_url']}")
                return

    def create_file(self, name: str, content: str) -> None:
        """Create a file with the given content."""
        (self.path / name).write_text(content)

    def create_dir(self, name: str) -> None:
        """Create a directory."""
        dir_path = self.path / name
        logger.debug(f"Creating directory {dir_path}")
        dir_path.mkdir(parents=True, exist_ok=True)

    def remove_file(self, name: str) -> None:
        """Remove a file."""
        logger.debug(f"Removing file {name}")
        os.remove(os.path.join(self.path, name))

    def remove_dir(self, name: str) -> None:
        """Remove a directory."""
        logger.debug(f"Removing directory {name or self.path}")
        if not name:
            shutil.rmtree(self.path)
        else:
            shutil.rmtree(os.path.join(self.path, name))

    def move_file_or_dir(self, src: str, dest: str) -> None:
        """Move a file or directory."""
        logger.debug(f"Moving file/dir {src} to {dest}")
        os.rename(os.path.join(self.path, src), os.path.join(self.path, dest))

    def move_all_files_in_dir(self, src: str, dest: str) -> None:
        """Move all files in a directory to another directory"""
        logger.debug(f"Moving all files in directory {src} to {dest}")
        for file in os.listdir(os.path.join(self.path, src)):
            os.rename(os.path.join(self.path, src, file), os.path.join(self.path, dest, file))

    def file_exists(self, name: str) -> bool:
        """Check if a file exists."""
        return (self.path / name).exists()

    def dir_exists(self, name: str) -> bool:
        """Check if a directory exists."""
        return (self.path / name).exists()

    def remove_line_in_file(self, contains: str | list, file: str):
        """Remove lines containing a specific string from a file."""
        target_file = self.path / file
        logger.debug(f"Removing lines containing {contains} in {target_file}")
        if isinstance(contains, list):
            for c in contains:
                self.bash(f"sed -i '/{c}/d' {target_file}")
        else:
            self.bash(f"sed -i '/{contains}/d' {target_file}")

    def replace_line_in_file(self, match: str, replace: str, file: str):
        """Replace lines containing a specific string in a file."""
        target_file = self.path / file
        logger.debug(f"Replacing lines containing {match} with {replace} in {target_file}")
        self.bash(f"sed -i 's/{match}/{replace}/g' {target_file}")
