# fastapi-vss, Apache-2.0 license
# Filename: app/start_worker.py
# Description: Run a worker to process tasks using RQ (Redis Queue) and Vision Transformer (ViT) models
import logging
import multiprocessing
import os

import redis

from app.logger import info
from app.predictors.tasks import MyWorker

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
logger.addHandler(console_handler)


def start_worker_for_project(project, redis_host, redis_port, password):
    # global predictors
    redis_conn = redis.Redis(host=redis_host, port=redis_port, password=password)
    info(f">>> Starting worker for project {project} <<<")
    worker = MyWorker(project, queues=["default"], connection=redis_conn)
    info(f">>> Worker for project {project} started <<<")
    worker.work()
    info(f">>> Worker for project {project} finished <<<")


if __name__ == "__main__":
    processes = []
    multiprocessing.set_start_method("spawn")

    from app.config import init_config

    config = init_config()

    for project, v_config in config.items():
        redis_host = v_config["redis_host"]
        redis_port = v_config["redis_port"]
        password = os.getenv("REDIS_PASSWD")
        p = multiprocessing.Process(target=start_worker_for_project, args=(project, redis_host, redis_port, password))
        p.start()
        processes.append(p)

    for p in processes:
        p.join()
