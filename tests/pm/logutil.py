
import logging
import sys


def log_to_stdout():
    logger = logging.getLogger()
    if not logger.hasHandlers():
        stream_handler = logging.StreamHandler(sys.stdout)
        logger.addHandler(stream_handler)


