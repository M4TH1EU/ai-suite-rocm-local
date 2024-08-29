import logging
import os
import shutil
import subprocess
import time

import psutil

from core import utils, config
from core.vars import logger, PYTHON_EXEC
from ui import choices


def find_correct_pid(parent_pid: int) -> int:
    processes: list[psutil.Process] = [psutil.Process(parent_pid)]
    create_time = processes[0].create_time()

    time.sleep(0.5)  # Wait for child processes to spawn

    for i in range(1, 10):
        if psutil.pid_exists(processes[0].pid + i):
            child_process = psutil.Process(processes[0].pid + i)
            if child_process.create_time() - create_time < 1:
                processes.append(psutil.Process(processes[0].pid + i))
        else:
            time.sleep(0.5 / i)

    return processes[-1].pid


class Stack:
    def __init__(self, name: str, id: str, port: int, url: str):
        self.name = name
        self.id = id
        self.path = os.path.join(os.path.expanduser("~"), ".ai-suite-rocm", id)

        self.url = url
        self.port = port

        self.pid = config.get(f"{self.name}-pid")


    def install(self):
        self.check_for_broken_install()
        self.create_venv()
        self._install()

        self.create_file('.installed', 'true')
        logger.info(f"Installed {self.name}")

    def _install(self):
        pass

    def is_installed(self):
        return self.file_exists('.installed')

    def check_for_broken_install(self):
        if not self.is_installed():
            if os.path.exists(self.path):
                if len(os.listdir(self.path)) > 0:
                    logger.warning("Found files from a previous/borked/crashed installation, cleaning up...")
                    self.bash(f"rm -rf {self.path}")
                    self.create_dir('')
            else:
                self.create_dir('')

    def update(self, folder: str = 'webui'):
        if self.is_installed():
            logger.info(f"Updating {self.name}")
            self.git_pull(folder)
        else:
            logger.warning(f"Could not update {self.name} as {self.name} is not installed")
            choices.any_key.ask()

    def uninstall(self):
        logger.info(f"Uninstalling {self.name}")
        self.bash(f"rm -rf {self.path}")

    def start(self):
        if self.is_installed():
            self._start()
        else:
            logger.error(f"{self.name} is not installed")
            choices.any_key.ask()

    def _start(self):
        pass

    def stop(self):
        if self.status():
            logger.debug(f"Killing {self.name} with PID: {self.pid}")
            psutil.Process(self.pid).kill()

        self.set_pid(None)

    def set_pid(self, pid):
        self.pid = pid
        if pid is not None:
            config.put(f"{self.name}-pid", pid)
        else:
            config.remove(f"{self.name}-pid")

    def restart(self):
        self.stop()
        self.start()

    def status(self) -> bool:
        if self.pid is None:
            return False

        return psutil.pid_exists(self.pid)

    # Python/Bash utils
    def create_venv(self):
        venv_path = os.path.join(self.path, 'venv')
        if not self.has_venv():
            logger.info(f"Creating venv for {self.name}")
            self.bash(f"{PYTHON_EXEC} -m venv {venv_path} --system-site-packages")
            self.pip_install("pip")
        else:
            logger.debug(f"Venv already exists for {self.name}")

    def has_venv(self) -> bool:
        return self.dir_exists('venv')

    def pip_install(self, package: str | list, no_deps: bool = False, env=[], args=[]):
        if no_deps:
            args.append("--no-deps")

        if isinstance(package, list):
            for p in package:
                logger.info(f"Installing {p}")
                self.pip(f"install -U {p}", env=env, args=args)
        else:
            logger.info(f"Installing {package}")
            self.pip(f"install -U {package}", env=env, args=args)

    def install_requirements(self, filename: str = 'requirements.txt', env=[]):
        logger.info(f"Installing requirements for {self.name} ({filename})")
        self.pip(f"install -r {filename}", env=env)

    def pip(self, cmd: str, env=[], args=[], current_dir: str = None):
        self.python(f"-m pip {cmd}", env=env, args=args, current_dir=current_dir)

    def python(self, cmd: str, env=[], args=[], current_dir: str = None, daemon: bool = False):
        self.bash(f"{' '.join(env)} {self.path}/venv/bin/python {cmd} {' '.join(args)}", current_dir, daemon)

    def bash(self, cmd: str, current_dir: str = None, daemon: bool = False):
        cmd = f"cd {self.path if current_dir is None else os.path.join(self.path, current_dir)} && {cmd}"

        if daemon:
            if self.status():
                choice = choices.already_running.ask()

                if choice is True:
                    self.stop()
                    self._start()
                    return
                else:
                    # TODO: attach to subprocess / redirect logs?
                    logger.info("Continuing without restarting...")
                    return
            else:
                logger.debug(f"Running command as daemon: {cmd}")
                cmd = f"{cmd} &"
                process = subprocess.Popen(cmd, shell=True, preexec_fn=os.setpgrp,
                                           stdout=config.open_file(f"{self.id}-stdout"),
                                           stderr=config.open_file(f"{self.id}-stderr"))
                self.set_pid(find_correct_pid(process.pid))
                return
        else:
            logger.debug(f"Running command: {cmd}")

            if logger.level == logging.DEBUG:
                process = subprocess.Popen(cmd, shell=True)
                process.wait()
                if process.returncode != 0:
                    raise Exception(f"Failed to run command: {cmd}")
            else:
                process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                out, err = process.communicate()

                if process.returncode != 0:
                    logger.fatal(f"Failed to run command: {cmd}")
                    logger.fatal(f"Error: {err.decode('utf-8')}")
                    logger.fatal(f"Output: {out.decode('utf-8')}")
                    raise Exception(f"Failed to run command: {cmd}")

    # Git utils
    def git_clone(self, url: str, branch: str = None, dest: str = None):
        logger.info(f"Cloning {url}")
        self.bash(f"git clone {f"-b {branch}" if branch is not None else ''} {url} {'' if dest is None else dest}")

    def git_pull(self, repo_folder: str, force: bool = False):
        self.bash(f"git reset --hard HEAD {'&& git clean -f -d' if force else ''} && git pull", repo_folder)

    # Prebuilt utils
    def install_from_prebuilt(self, name):
        for prebuilt in utils.get_prebuilts():
            if prebuilt['name'].split("-")[0] == name:
                self.pip(f"install {prebuilt['browser_download_url']}")
                return

    # File utils
    def create_file(self, name, content):
        with open(os.path.join(self.path, name), 'w') as f:
            f.write(content)

    def create_dir(self, name):
        if name == '':
            logger.info(f"Creating directory for {self.name}")

        logger.debug(f"Creating directory {name}")
        os.makedirs(os.path.join(self.path, name), exist_ok=True)

    def remove_file(self, name):
        logger.debug(f"Removing file {name}")
        os.remove(os.path.join(self.path, name))

    def remove_dir(self, name):
        logger.debug(f"Removing directory {name}")
        shutil.rmtree(os.path.join(self.path, name))

    def move_file_or_dir(self, src, dest):
        logger.debug(f"Moving file/dir {src} to {dest}")
        os.rename(os.path.join(self.path, src), os.path.join(self.path, dest))

    def move_all_files_in_dir(self, src, dest):
        logger.debug(f"Moving all files in directory {src} to {dest}")
        for file in os.listdir(os.path.join(self.path, src)):
            os.rename(os.path.join(self.path, src, file), os.path.join(self.path, dest, file))

    def file_exists(self, name):
        return os.path.exists(os.path.join(self.path, name))

    def dir_exists(self, name):
        return os.path.exists(os.path.join(self.path, name))

    def remove_line_in_file(self, contains: str | list, file: str):
        logger.debug(f"Removing lines containing {contains} in {file}")

        if isinstance(contains, list):
            for c in contains:
                self.bash(f"sed -i '/{c}/d' {file}")
        else:
            self.bash(f"sed -i '/{contains}/d' {file}")

    def replace_line_in_file(self, match: str, replace: str, file: str):
        logger.debug(f"Replacing lines containing {match} with {replace} in {file}")
        self.bash(f"sed -i 's/{match}/{replace}/g' {file}")
