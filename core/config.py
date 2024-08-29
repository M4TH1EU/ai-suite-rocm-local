import json
import os

from core.vars import logger

data = {}
file = os.path.join(os.path.expanduser("~"), ".config", "ai-suite-rocm", "config.json")


def create():
    if not os.path.exists(file):
        os.makedirs(os.path.dirname(file), exist_ok=True)
        with open(file, "w") as f:
            f.write("{}")

        logger.info(f"Created config file at {file}")


def read():
    global data
    with open(file, "r") as f:
        data = json.load(f)


def write():
    global data
    with open(file, "w") as f:
        json.dump(data, f)


def get(key: str, default=None):
    global data
    if key not in data:
        return default

    return data.get(key)


def put(key: str, value):
    global data
    data[key] = value
    write()


def has(key: str):
    global data
    return key in data


def remove(key: str):
    global data
    if key in data:
        data.pop(key)
    write()


def clear():
    global data
    data = {}
    write()


def create_file(filename: str, content: str):
    with open(os.path.join(os.path.dirname(file), filename), "w") as f:
        f.write(content)


def remove_file(filename: str):
    os.remove(os.path.join(os.path.dirname(file), filename))


def file_exists(filename: str):
    return os.path.exists(os.path.join(os.path.dirname(file), filename))


def get_file_path(filename: str):
    return os.path.join(os.path.dirname(file), filename)


def open_file(filename: str, mode: str = 'w'):
    return open(os.path.join(os.path.dirname(file), filename), mode)
