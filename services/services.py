import logging
import os
import subprocess

import psutil

import main
import utils
from main import PYTHON_EXEC, logger, get_config


class Stack:
    def __init__(self, name: str, path: str, port: int, url: str):
        self.name = name
        self.path = os.path.join(os.path.expanduser("~"), ".ai-suite-rocm", path)

        self.url = url
        self.port = port

        self.process = None


    def install(self):
        self.create_file('.installed', 'true')
        logger.info(f"Installed {self.name}")

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
        if self.dir_exists(folder):
            logger.info(f"Updating {self.name}")
            self.git_pull(folder)
        else:
            logger.warning(f"Could not update {self.name} as {folder} does not exist")

    def uninstall(self):
        self.bash(f"rm -rf {self.path}")

    def start(self):
        if self.is_installed():
            self.update()
        else:
            self.check_for_broken_install()
            self.create_venv()
            self.install()

        self._launch()

    def _launch(self):
        pass

    def stop(self):
        pass

    def restart(self):
        self.stop()
        self.start()

    def status(self) -> bool:
        pass

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
        self.bash(f"{' '.join(env)} {self.path}/venv/bin/pip {cmd} {' '.join(args)}", current_dir)

    def python(self, cmd: str, env=[], current_dir: str = None, daemon: bool = False):
        self.bash(f"{' '.join(env)} {self.path}/venv/bin/python {cmd}", current_dir, daemon)

    def bash(self, cmd: str, current_dir: str = None, daemon: bool = False):
        cmd = f"cd {self.path if current_dir is None else os.path.join(self.path, current_dir)} && {cmd}"

        if daemon:
            # Check if previous run process is saved
            if get_config().has(f"{self.name}-pid"):

                # Check if PID still running
                if psutil.pid_exists(main.config.get(f"{self.name}-pid")):
                    choice = input(f"{self.name} is already running, do you want to restart it? (y/n): ")

                    if choice.lower() == 'y':
                        pid = main.config.get(f"{self.name}-pid")
                        logger.debug(f"Killing previous daemon with PID: {pid}")
                        psutil.Process(pid).kill()
                    else:
                        # TODO: attach to subprocess?
                        return
                else:
                    logger.warning(
                        f"Previous PID found for {self.name} but process is not running, continuing as stopped...")
            else:
                logger.debug(f"No previous PID found for {self.name}, continuing as stopped...")

            logger.debug(f"Starting {self.name} as daemon with command: {cmd}")
            cmd = f"{cmd} &"
            process = subprocess.Popen(cmd, shell=True)
            get_config().set(f"{self.name}-pid", process.pid + 1)
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
        os.rmdir(os.path.join(self.path, name))

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
