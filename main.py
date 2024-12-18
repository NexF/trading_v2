#!/usr/bin/env python

import logging
import sys

import colorlog

import base_frame

LOGGING_CONFIG = {
    "DEBUG": {"color": "purple"},
    "INFO": {"color": "green"},
    "WARNING": {"color": "yellow"},
    "ERROR": {"color": "red"},
    "CRITICAL": {"color": "bold_red"},
}


def setup_logging() -> None:
    logger = logging.getLogger("tframe")
    logger.setLevel(logging.INFO)
    format = colorlog.ColoredFormatter(
        "%(log_color)s[%(asctime)-15s][%(levelname)8s]%(reset)s - %(message)s",
        log_colors={key: conf["color"] for key, conf in LOGGING_CONFIG.items()},
    )
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(format)
    logger.addHandler(handler)


if __name__ == "__main__":
    setup_logging()

    base_frame.init()
