# fastapi-vss, Apache-2.0 license
# Filename: predictors/tasks.py
# Description: Worker task file for processing images with Vision Transformer (ViT) models
import gc
import json
import os
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
        # Save to output_json file using the first and last filename(if there is more than one filename)
        file_stem = f"{os.path.splitext(os.path.basename(filenames[0]))[0]}_to_{os.path.splitext(os.path.basename(filenames[-1]))[0]}" if len(filenames) > 1 else os.path.splitext(os.path.basename(filenames[0]))[0]
        output_json = f"{v_config['output_dir']}/{file_stem}.json"
        debug(f"Saving predictions to {file_stem}.json")
        with open(output_json, 'w') as f:
            json.dump({
                "filenames": filenames,
                "predictions": predictions,
                "scores": scores,
                "ids": ids
            }, f, indent=4)
        debug(f"Predictions saved to {output_json}")
    except Exception as e:
        error_message = f"Error saving predictions to {output_json}: {e}"
        info(error_message)
        return error_message
