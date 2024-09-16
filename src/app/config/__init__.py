# fastapi-vss, Apache-2.0 license
# Filename: app/config/__init__.py
# Description:  Configuration for the application.
# This needs to be imported first in order to set up the logger and other configuration.

from pathlib import Path
import tempfile

import redis
import yaml
import os
import dotenv

from app.logger import info
from aidata.predictors.process_vits import ViTWrapper

"""
Initialize the configuration for the application
"""

# Number of images to process in a batch
BATCH_SIZE = 8

# Path to store temporary files
temp_path = Path(tempfile.gettempdir()) / 'fastapi-vss'

# Required environment variables REDIS_PASSWD and CONFIG_PATH
dotenv.load_dotenv()
if not os.getenv("REDIS_PASSWD"):
    raise Exception("REDIS_PASSWD environment variable not set")
if not os.getenv("CONFIG_PATH"):
    raise Exception("CONFIG_PATH environment variable not set")

config_path = Path(os.getenv("CONFIG_PATH"))

def init_config() -> dict:
    """
    Initialize the configuration for the application
    :return: Dictionary of configuration settings keyed by project name
    """
    config = {}
    # Read the yaml configuration files for each project
    for yaml_path in config_path.rglob('*.yml'):
        if not yaml_path.exists():
            raise FileNotFoundError(f"Could not find {yaml_path}")

        # Read the yaml configuration files for each project
        with yaml_path.open('r') as yaml_file:
            data = yaml.safe_load(yaml_file)
            info(f"Reading configuration from {yaml_path}")
            info(data)
            redis_host = data['redis']['host']
            redis_port = data['redis']['port']
            model = data['vss']['model']
            password = os.getenv("REDIS_PASSWD")

            info(f"Connecting to redis at {redis_host}:{redis_port}")
            r = redis.Redis(host=redis_host, port=redis_port, password=password)
            v = ViTWrapper(r, device="cpu", model_name=model, reset=False, batch_size=BATCH_SIZE)

            project = data['vss']['project']

            config[project] = {
                'redis_host': redis_host,
                'redis_port': redis_port,
                'r': r,
                'v': v,
            }
    return config
