# fastapi-vss, Apache-2.0 license
# Filename: app/conf/init.py
# Description:  Logger for fastapi-vss. Logs to both a file and the console

import logging
from pathlib import Path
from datetime import datetime as dt

LOGGER_NAME = "FASTAPI_VSS"
DEBUG = True


class _Singleton(type):
    """A metaclass that creates a Singleton base class when called."""

    instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls.instances:
            cls.instances[cls] = super(_Singleton, cls).__call__(*args, **kwargs)
        return cls.instances[cls]


class Singleton(_Singleton("SingletonMeta", (object,), {})):
    pass


class CustomLogger(Singleton):
    _logger = None
    _output_path = Path.cwd()

    def __init__(self, output_path: Path = Path.cwd(), output_prefix: str = "fastapi_vss"):
        """
        Initialize the logger
        """
        self._logger = logging.getLogger(LOGGER_NAME)
        self._logger.setLevel(logging.DEBUG)
        self._output_path = output_path
        output_path.mkdir(parents=True, exist_ok=True)
        formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s")

        # default log file date to today
        now = dt.utcnow()

        # log to file
        log_filename = output_path / f"{output_prefix}_{now:%Y%m%d}.log"
        handler = logging.FileHandler(log_filename, mode="w")
        handler.setFormatter(formatter)
        handler.setLevel(logging.INFO)
        self._logger.addHandler(handler)

        # also log to console
        console = logging.StreamHandler()
        console.setLevel(logging.DEBUG)
        console.setFormatter(formatter)
        self._logger.addHandler(console)

        self._logger.info(f"Logging to {log_filename}")

    def loggers(self) -> logging.Logger:
        return self._logger


def create_logger_file(log_path: Path, prefix: str = "fastapi_vss"):
    """
    Create a logger file
    :param log_path: Path to the log file
    """
    # create the log directory if it doesn't exist
    log_path.mkdir(parents=True, exist_ok=True)
    return CustomLogger(log_path, prefix)


def custom_logger() -> logging.Logger:
    """
    Get the logger
    """
    return logging.getLogger(LOGGER_NAME)


def err(s: str):
    custom_logger().error(s)


def info(s: str):
    custom_logger().info(s)


def debug(s: str):
    custom_logger().debug(s)


def warn(s: str):
    custom_logger().warning(s)


def exception(s: str):
    custom_logger().exception(s)


def critical(s: str):
    custom_logger().critical(s)
