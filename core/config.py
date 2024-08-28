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


def get(key: str):
    global data
    return data.get(key)


def set(key: str, value):
    global data
    data[key] = value
    write()


def has(key: str):
    global data
    return key in data


def remove(key: str):
    global data
    data.pop(key)
    write()


def clear():
    global data
    data = {}
    write()
