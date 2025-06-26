# fastapi-vss, Apache-2.0 license
# Filename: app/config/__init__.py
# Description:  Configuration for the application.
# This needs to be imported first in order to set up the logger and other configuration.

from pathlib import Path
import tempfile

from typing import TypedDict, Any
import torch
import yaml
import os
import dotenv
from torch import device

from app.logger import info

"""
Initialize the configuration for the application
"""

# Number of images to process in a batch to default 32, or can be set by the environment variable BATCH_SIZE
BATCH_SIZE = int(os.getenv("BATCH_SIZE", 32))

# Path to store temporary files
temp_path = Path(tempfile.gettempdir()) / "fastapi-vss"

# Required environment variables REDIS_PASSWD and CONFIG_PATH
dotenv.load_dotenv()
if not os.getenv("REDIS_PASSWD"):
    raise Exception("REDIS_PASSWD environment variable not set")
if not os.getenv("CONFIG_PATH"):
    raise Exception("CONFIG_PATH environment variable not set")

CONFIG_PATH = Path(os.getenv("CONFIG_PATH"))


class VConfig(TypedDict):
    redis_port: str
    redis_host: int
    device: torch.device
    model: str
    project: str


def init_config() -> dict[Any, dict[str, device | Any]]:
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

            config[project] = {
                "redis_host": data["redis"]["host"],
                "redis_port": data["redis"]["port"],
                "model": data["vss"]["model"],
                "device": device,
                "project": project,
                "output_dir":  data["vss"]["output_dir"]
            }

    return config
