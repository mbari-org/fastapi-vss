# fastapi-vss, Apache-2.0 license
# Filename: app/main.py
# Description: Process images with Vision Transformer (ViT) models
import os

import redis
import torch
import pynvml

from fastapi import FastAPI, status, File, UploadFile
from typing import List

from rq import Queue
from rq.job import Job

from app import __version__
from app import logger
from app.config import init_config, BATCH_SIZE
from app.logger import info, debug
from app.predictors.tasks import predict_on_cpu_or_gpu
from app.predictors.vector_similarity import VectorSimilarity

log_path = os.getenv("LOG_DIR", "logs")
logger = logger.create_logger_file(log_path)

info(f"Starting Fast-VSS API version {__version__}")

app = FastAPI(
    title=f"Fast-VSS API version {__version__}",
    description=f"""Run vector similarity search using Vision Transformer (ViT) models . Version {__version__}""",
    version=__version__,
)

info("Loading configuration")
config = init_config()

if len(config) == 0:
    raise Exception("No projects found in the configuration file")

queues = {}
connections = {}

for project in config.keys():
    redis_host = config[project]["redis_host"]
    redis_port = config[project]["redis_port"]
    device = config[project]["device"]
    password = os.getenv("REDIS_PASSWD")
    info(f"Connecting to redis at {redis_host}:{redis_port}")
    redis_conn = redis.Redis(host=redis_host, port=redis_port, password=password)
    connections[project] = redis_conn
    info(f"Creating Redis queue for project {project}")
    redis_queue = Queue(connection=redis_conn)
    info(f"Redis queue for project {project} created successfully")
    queues[project] = redis_queue

DEFAULT_PROJECT = list(config.keys())[0]

GPU_AVAILABLE = False
if torch.cuda.is_available():
    pynvml.nvmlInit()
    GPU_AVAILABLE = True


@app.get("/")
async def root():
    return {"message": f"Welcome to Fast-VSS API version {__version__}"}


@app.get("/health", status_code=status.HTTP_200_OK)
async def health():
    """
    Health check endpoint to verify if the API is running
    """
    return {"status": "ok", "version": __version__}


@app.get("/gpu-memory")
def gpu_memory():
    if not GPU_AVAILABLE:
        return {"error": "No GPU available"}
    handle = pynvml.nvmlDeviceGetHandleByIndex(0)  # GPU 0
    mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
    return {"used_memory": mem_info.used, "total_memory": mem_info.total}


@app.get("/projects")
async def get_projects():
    return {"projects": list(config.keys())}


@app.get("/ids/{project}", status_code=status.HTTP_200_OK)
async def get_ids(project: str = DEFAULT_PROJECT):
    # Check if the project name is in the config
    if project not in config.keys():
        return {"error": f"Invalid project name {project}"}

    try:
        # Connect to the Redis queue for the project
        redis_conn = connections[project]
        info(f"Fetching IDs for project {project}")
        all_keys = redis_conn.keys(f"{VectorSimilarity.DOC_PREFIX}*")
        # Data is formatted <doc:label:id>, e.g. doc:Otter:12467, doc:Otter:12467, etc.
        classes = []
        ids = []
        for i, key in enumerate(all_keys):
            str = key.decode("utf-8").split(":")
            if len(str) == 3:
                classes.append(str[1])
                ids.append(str[2])

        return {"ids": ids, "classes": classes}
    except Exception as e:
        return {"error": f"Error getting ids: {e}"}


@app.post("/knn/{top_n}/{project}", status_code=status.HTTP_200_OK)
async def knn(files: List[UploadFile] = File(...), top_n: int = 1, project: str = DEFAULT_PROJECT):
    try:
        # Check if the project name is in the config
        if project not in config.keys():
            return {"error": f"Invalid project name {project}"}

        info(f"Predicting {len(files)} for top {top_n} in project {project}")
        if len(files) > BATCH_SIZE:
            return {"error": f"Images should be less than batch size {BATCH_SIZE}"}

        if top_n == 0:
            return {"error": "Please provide a valid top_n value greater than 0"}

        images = [f.file for f in files]
        filenames = [f.filename for f in files]
        redis_queue = queues[project]

        info(f"Enqueuing job for {len(images)} images with top_n={top_n} in project {project}")
        vss_config = config[project]
        job = redis_queue.enqueue(predict_on_cpu_or_gpu, vss_config, images, top_n, filenames)
        job_id = job.get_id()
        debug(f"Enqueued job with ID {job_id} for project {project}")
        return {"job_id": job_id, "Comment": f"Job results will be available for 5 minutes after completion. Use /predict/job/{job_id}/{project} to check status."}
    except Exception as e:
        return {"error": f"Error predicting images: {e}"}


@app.get("/predict/job/{job_id}/{project}")
async def get_job_result(job_id: str, project: str = DEFAULT_PROJECT):
    if project not in config.keys():
        return {"error": f"Invalid project name {project}"}

    try:
        # Check if the job ID is valid
        if not Job.exists(job_id, connection=connections[project]):
            return {"error": f"Job ID {job_id} does not exist in project {project}"}

        redis_conn = connections[project]
        info(f"Fetching job status for job ID {job_id} in project {project}")
        job = Job.fetch(job_id, connection=redis_conn)
        if job.is_finished:
            return {"status": "done", "result": job.return_value()}
        elif job.is_failed:
            return {"status": "failed"}
        else:
            return {"status": "pending"}
    except Exception as e:
        return {"error": f"Error fetching job status: {e}"}
