# fastapi-vss, Apache-2.0 license
# Filename: app/config/__init__.py
# Description:  Configuration for the application.
# This needs to be imported first in order to set up the logger and other configuration.
import logging
from pathlib import Path

from typing import TypedDict, Any
import torch
import yaml
import os
import dotenv
from torch import device

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
logger.addHandler(console_handler)
info = logger.info
debug = logger.debug
err = logger.error


# Required environment variables REDIS_PASSWD and CONFIG_PATH
dotenv.load_dotenv()
if not os.getenv("REDIS_PASSWD"):
    raise Exception("REDIS_PASSWD environment variable not set")
if not os.getenv("CONFIG_PATH"):
    raise Exception("CONFIG_PATH environment variable not set")

# Number of images to process in a batch to default 32, or can be set by the environment variable BATCH_SIZE
BATCH_SIZE = int(os.getenv("BATCH_SIZE", 32))

# Get the path of this file
CONFIG_PATH = Path(os.getenv("CONFIG_PATH"), Path(__file__).parent.parent.parent.parent / "config")

print(f"Using configuration path: {CONFIG_PATH}")


class VConfig(TypedDict):
    redis_port: str
    redis_host: int
    device: torch.device
    model: str
    project: str


def init_config(target_project=None) -> dict[Any, dict[str, device | Any]]:
    """
    Initialize the configuration for the application
    :return: Dictionary of configuration settings keyed by project name
    """
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    config = {}
    # Read the yaml configuration files for each project
    for yaml_path in CONFIG_PATH.rglob("*.yml"):
        if not yaml_path.exists():
            raise FileNotFoundError(f"Could not find {yaml_path}")

        # Read the yaml configuration files for each project and setup the output directory
        with yaml_path.open("r") as yaml_file:
            data = yaml.safe_load(yaml_file)
            info(f"Reading configuration from {yaml_path}")
            info(data)
            project = data["vss"]["project"]
            if target_project and project != target_project:
                continue

            config[project] = {
                "redis_host": data["redis"]["host"],
                "redis_port": data["redis"]["port"],
                "model": data["vss"]["model"],
                "device": device,
                "project": project,
                "output_path": data["vss"]["output_path"],
            }

    return config
