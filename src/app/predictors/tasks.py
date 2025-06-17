# fastapi-vss, Apache-2.0 license
# Filename: predictors/tasks.py
# Description: Worker task file for processing images with Vision Transformer (ViT) models
import gc
from typing import List

from app.logger import err, info, debug
from transformers import AutoModelForImageClassification, AutoImageProcessor  # type: ignore
from app.predictors.process_vits import ViTWrapper


def create_model_from_config(config: dict, device: str = "cpu") ->  ViTWrapper:
    """
    Create a ViTWrapper model from the provided configuration.

    :param config: Configuration dictionary containing Redis connection details and model parameters.
    :param device: Device to use for processing (e.g., "cpu" or "cuda:0").
    :return: An instance of ViTWrapper.
    """
    global BATCH_SIZE
    return ViTWrapper(config['redis_conn'], device=device, model_name=config['model'], reset=False, batch_size=BATCH_SIZE)


def predict_on_cpu_or_gpu(v_config:dict, image_bytes_list: List[bytes], top_n: int):
    info(f"Predicting on {len(image_bytes_list)} images with top_n={top_n} using model {v_config['model']} on device {v_config['device']}")
    return {
        "predictions": [],
        "scores": [],
        "ids": [],
    }
    # v = create_model_from_config(v_config, device=v_config['device'])
    # predictions, scores, ids = v.predict(images, top_n)
    # if v_config['device'] == 'cuda:0':
    #     v.free_gpu_memory()
    # gc.collect()
    # del images
    # return {
    #     "predictions": predictions,
    #     "scores": scores,
    #     "ids": ids,
    # }