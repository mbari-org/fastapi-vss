# fastapi-vss, Apache-2.0 license
# Filename: app/start_worker.py
# Description: Run a worker to process tasks using RQ (Redis Queue) and Vision Transformer (ViT) models
import logging
import multiprocessing
import os
import time

import redis

from app.logger import info
from app.predictors.tasks import MyWorker

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
# Suppress verbose PIL/Pillow PNG stream debug logs
logging.getLogger("PIL").setLevel(logging.WARNING)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
logger.addHandler(console_handler)

# Retry settings for connecting to Redis (handles startup race in Docker)
REDIS_CONNECT_TIMEOUT = int(os.getenv("REDIS_CONNECT_TIMEOUT", "10"))
REDIS_CONNECT_RETRIES = int(os.getenv("REDIS_CONNECT_RETRIES", "30"))
REDIS_CONNECT_RETRY_DELAY = float(os.getenv("REDIS_CONNECT_RETRY_DELAY", "2.0"))


def _redis_connection_with_retry(host, port, password):
    """Create a Redis connection, retrying with backoff until Redis is ready."""
    last_error = None
    for attempt in range(1, REDIS_CONNECT_RETRIES + 1):
        try:
            conn = redis.Redis(
                host=host,
                port=port,
                password=password,
                socket_connect_timeout=REDIS_CONNECT_TIMEOUT,
            )
            conn.ping()
            return conn
        except (redis.exceptions.TimeoutError, redis.exceptions.ConnectionError, OSError) as e:
            last_error = e
            logger.warning(f"Redis connection {host} attempt {attempt}/{REDIS_CONNECT_RETRIES} failed: {e}")
            time.sleep(REDIS_CONNECT_RETRY_DELAY)
    raise last_error


def start_worker_for_project(project, redis_host, redis_port, password):
    # Set CUDA optimizations
    import torch

    if torch.cuda.is_available():
        torch.backends.cudnn.benchmark = True
        torch.backends.cudnn.deterministic = False

    # global predictors
    redis_conn = _redis_connection_with_retry(redis_host, redis_port, password)
    info(f">>> Starting worker for project {project} <<<")
    worker = MyWorker(project, queues=["default"], connection=redis_conn)
    info(f">>> Worker for project {project} started <<<")
    worker.work()
    info(f">>> Worker for project {project} finished <<<")


if __name__ == "__main__":
    processes = []
    multiprocessing.set_start_method("spawn")

    from app.config import init_config

    try:
        config = init_config()

        if len(config) == 0:
            raise Exception("No projects found in the configuration file")

        for project, v_config in config.items():
            redis_host = v_config["redis_host"]
            redis_port = v_config["redis_port"]
            password = os.getenv("REDIS_PASSWD")
            p = multiprocessing.Process(target=start_worker_for_project, args=(project, redis_host, redis_port, password))
            p.start()
            processes.append(p)

        for p in processes:
            p.join()
    except Exception as e:
        logger.error(f"Error starting worker processes: {e}")
        raise

    logger.info("All worker processes completed.")
