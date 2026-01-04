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
import httpx
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

# Cache for remote configs fetched from URLs to avoid repeated network calls
_remote_config_cache: dict[str, dict] = {}


class VConfig(TypedDict):
    redis_port: str
    redis_host: int
    device: torch.device
    model: str
    project: str


def _deep_merge_dict(base: dict, override: dict) -> dict:
    """
    Deep merge two dictionaries, with override values taking precedence.
    :param base: Base dictionary
    :param override: Dictionary with values that override base
    :return: Merged dictionary
    """
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge_dict(result[key], value)
        else:
            result[key] = value
    return result


def _fetch_config_from_url(url: str) -> dict:
    """
    Fetch YAML configuration from a URL with caching to avoid repeated network calls.
    :param url: URL to fetch the configuration from
    :return: Parsed YAML configuration as a dictionary
    """
    # Check cache first
    if url in _remote_config_cache:
        info(f"Using cached configuration from URL: {url}")
        return _remote_config_cache[url]
    
    try:
        info(f"Fetching configuration from URL: {url}")
        with httpx.Client(timeout=30.0) as client:
            response = client.get(url)
            response.raise_for_status()
            remote_data = yaml.safe_load(response.text)
            # Cache the fetched config
            _remote_config_cache[url] = remote_data
            info(f"Successfully fetched and cached configuration from {url}")
            return remote_data
    except httpx.HTTPError as e:
        err(f"Failed to fetch configuration from {url}: {e}")
        raise Exception(f"Failed to fetch configuration from URL: {url}") from e
    except yaml.YAMLError as e:
        err(f"Failed to parse YAML from {url}: {e}")
        raise Exception(f"Invalid YAML in configuration URL: {url}") from e


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

        # Read the local yaml configuration file
        with yaml_path.open("r") as yaml_file:
            local_data = yaml.safe_load(yaml_file)
            info(f"Reading configuration from {yaml_path}")
            info(local_data)
            
            # Check if config_url is specified
            config_url = local_data.get("config_url")
            if config_url:
                # Fetch remote configuration and merge with local (remote overrides local)
                remote_data = _fetch_config_from_url(config_url)
                # Remove config_url from local_data before merging (it's not part of the actual config)
                local_data_without_url = {k: v for k, v in local_data.items() if k != "config_url"}
                # Merge remote config over local config
                data = _deep_merge_dict(local_data_without_url, remote_data)
                info(f"Merged remote configuration from {config_url} with local configuration")
            else:
                data = local_data
            
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
