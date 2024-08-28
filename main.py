import logging
import os
import sys

PYTHON_EXEC = 'python3.10'
PATH = os.path.dirname(os.path.abspath(__file__))
ROCM_VERSION = "6.1.2"

# Set up logging
LEVEL = logging.DEBUG
logger = logging.getLogger('ai-suite-rocm')
if not logger.hasHandlers():
    handler_with_formatter = logging.StreamHandler(stream=sys.stdout)
    handler_with_formatter.setFormatter(logging.Formatter('[%(levelname)s] : %(message)s'))
    logger.addHandler(handler_with_formatter)
logger.setLevel(LEVEL)

if __name__ == '__main__':
    logger.info("Starting AI Suite for ROCM")

    from services import TextGeneration

    test = TextGeneration().start()
