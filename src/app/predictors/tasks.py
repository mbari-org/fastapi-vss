# fastapi-vss, Apache-2.0 license
# Filename: predictors/tasks.py
# Description: Worker task file for processing images with Vision Transformer (ViT) models
import gc
import json
import os
from datetime import datetime
from pathlib import Path
from typing import List

import redis

from app.logger import info, debug
from app.predictors.process_vits import ViTWrapper
from app.config import BATCH_SIZE, init_config

config = init_config()
predictors = {}
initialized = False


def init_predictors() -> dict[str, ViTWrapper]:
    """
    Initialize predictors for each project defined in the configuration.
    Connects to Redis and sets up the ViTWrapper for each project.
    """
    global predictors, initialized
    if initialized:
        return predictors

    info("Initializing predictors...")

    if not config:
        raise ValueError("Configuration is empty. Please check your config file.")

    password = os.getenv("REDIS_PASSWD")
    if not password:
        raise ValueError("REDIS_PASSWD environment variable is not set. Please set it to connect to Redis.")

    info(f"Found {len(config.keys())} projects in the configuration.")
    for project in config.keys():
        redis_host = config[project]["redis_host"]
        redis_port = config[project]["redis_port"]
        v_config = config[project]
        info(f"Connecting to redis at {redis_host}:{redis_port}")
        info(f"Redis queue for project {project} created successfully")
        redis_conn = redis.Redis(host=redis_host, port=redis_port, password=password)
        predictors[project] = ViTWrapper(redis_conn, device=v_config["device"], model_name=v_config["model"], reset=False, batch_size=BATCH_SIZE)

    initialized = True
    return predictors


def predict_on_cpu_or_gpu(v_config: dict, image_list: List[str], top_n: int, filenames: List[str]):
    info(f"Predicting on {len(image_list)} images with top_n={top_n} using model {v_config['model']} on device {v_config['device']}")

    global predictors
    if not predictors:
        init_predictors()
    v = predictors.get(v_config.get("project"))
    if not v:
        message = f"Predictor for project {v_config.get('project')} not found. Please initialize predictors first."
        info(message)
        return message

    try:
        predictions, scores, ids = v.predict(image_list, top_n)
        gc.collect()
        del image_list

        # Make a subdirectory based on the current date and time (hourly granularity)
        current_time_hr = datetime.now().strftime("%Y%m%d_%H0000")
        current_time = datetime.now().strftime("%Y%m%d_%H%M%S.%f")

        # Create output directory if it doesn't exist
        output_dir = v_config.get("output_dir", "output")
        output_path = Path(output_dir) / current_time_hr
        output_path.mkdir(parents=True, exist_ok=True)
        output_json = output_path / f"{current_time}.json"

        debug(f"Saving predictions to {current_time}.json")
        with output_json.open("w") as f:
            json.dump({
                "filenames": filenames,
                "predictions": predictions,
                "scores": scores,
                "ids": ids
            }, f, indent=4)
        debug(f"Predictions saved to {output_json}")
    except Exception as e:
        error_message = f"Error saving predictions: {e}"
        info(error_message)
        return error_message
