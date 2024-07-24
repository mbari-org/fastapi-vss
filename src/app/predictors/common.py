# aipipeline, Apache-2.0 license
# Filename: predictors/common.py
# Description: Common functions
import os
import yaml

from tator.openapi.tator_openapi import TatorApi
from tator.openapi.tator_openapi.models import Project
import tator

from aipipeline.logger import info, debug, err

def init_yaml_config(yaml_config: str) -> dict:
    """
    # Get the configuration from the YAML file
    :param yaml_config: The YAML configuration file
    :return: The configuration dictionary
    """
    info(f"Reading configuration from {yaml_config}")
    if not os.path.exists(yaml_config):
        info(f"Configuration file {yaml_config} not found")
        raise FileNotFoundError(f"Configuration file {yaml_config} not found")
    with open(yaml_config, "r") as file:
        try:
            config_dict = yaml.safe_load(file)
        except yaml.YAMLError as e:
            err("Error reading YAML file:", e)
            raise e
    return config_dict
