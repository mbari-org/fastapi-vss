# fastapi-vss, Apache-2.0 license
# Filename: app/config/__init__.py
# Description:  Configuration for the application.
# This needs to be imported first in order to set up the logger and other configuration.

from pathlib import Path
import tempfile

import redis
import yaml

from app.logger import info
from submodules.aidata.aidata.predictors.process_vits import ViTWrapper

"""
Initialize the configuration for the application
"""

# Number of images to process in a batch
BATCH_SIZE = 8

# Path to store temporary files
temp_path = Path(tempfile.gettempdir()) / 'fastapi-vss'

config_path = Path(__file__).parent.parent.parent / 'submodules' / 'aidata' /  'aidata' / 'config'


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
            redis_host = data['redis']['host']
            redis_port = data['redis']['port']

            info(f"Connecting to redis at {redis_host}:{redis_port}")
            r = redis.Redis(host=redis_host, port=redis_port, password=data['redis']['password'])
            v = ViTWrapper(r, "cpu", False, BATCH_SIZE)

            project = data['tator']['project']

            config[project] = {
                'redis_host': redis_host,
                'redis_port': redis_port,
                'r': r,
                'v': v,
            }
    return config
