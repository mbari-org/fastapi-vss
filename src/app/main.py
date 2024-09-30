# fastapi-vss, Apache-2.0 license
# Filename: app/main.py
# Description: Process images with foundational Vision Transformer (ViT) models
import os
from pathlib import Path

from fastapi import FastAPI, status, File, UploadFile
from typing import List

from app import __version__
from app import logger
from app.logger import info
from config import init_config, BATCH_SIZE

logger = logger.create_logger_file(Path("logs"))

info(f"Starting Fast-VSS API version {__version__}")

app = FastAPI(
    title=f"Fast-VSS API version {__version__}",
    description=f"""Run vector similarity search using foundational Vision Transformer (ViT) models . Version {__version__}""",
    version=__version__,
)

info("Loading configuration")
global_config = init_config()

if len(global_config) == 0:
    raise Exception("No projects found in the configuration file")

DEFAULT_PROJECT = list(global_config.keys())[0]


@app.get("/")
async def root():
    return {"message": f"Welcome to Fast-VSS API version {__version__}"}


@app.get("/projects")
async def get_projects():
    return {"projects": list(global_config.keys())}

@app.post("/ids/{project}", status_code=status.HTTP_200_OK)
async def get_ids(project: str = DEFAULT_PROJECT):
    # Check if the project name is in the config
    if project not in global_config.keys():
        return {"error": f"Invalid project name {project}"}

    v = global_config[project]['v']
    try:
        classes, ids = v.get_ids()
        return {"ids": ids, "classes": classes}
    except Exception as e:
        return {"error": f"Error getting ids: {e}"}

@app.post("/knn/{top_n}/{project}", status_code=status.HTTP_200_OK)
async def knn(files: List[UploadFile] = File(...), top_n: int = 1, project: str = DEFAULT_PROJECT):
    try:
        info(f"Predicting {len(files)} for top {top_n} in project {project}")
        if len(files) > BATCH_SIZE:
            return {"error": f"Images should be less than batch size {BATCH_SIZE}"}

        if top_n == 0:
            return {"error": f"Please provide a valid top_n value greater than 0"}

        # Check if the project name is in the config
        if project not in global_config.keys():
            return {"error": f"Invalid project name {project}"}

        v = global_config[project]['v']
        images = [f.file for f in files]
        predictions, scores, ids = v.predict(images, top_n)
        return {"predictions": predictions, "scores": scores, "ids": ids}
    except Exception as e:
        return {"error": f"Error predicting images: {e}"}
