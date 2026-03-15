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

    # #region agent log
    import json as _dj
    import time as _dt
    import socket as _ds
    import subprocess as _dsp
    import ctypes as _dc
    import ctypes.util as _dcu

    _DPATH = "/tmp/debug-31e49a.log"

    def _dbg(msg, data, hyp):
        try:
            with open(_DPATH, "a") as _f:
                _f.write(
                    _dj.dumps(
                        {
                            "sessionId": "31e49a",
                            "timestamp": int(_dt.time() * 1000),
                            "location": "start_worker.py:start_worker_for_project",
                            "message": msg,
                            "data": data,
                            "hypothesisId": hyp,
                            "host": _ds.gethostname(),
                            "project": project,
                        }
                    )
                    + "\n"
                )
        except Exception:
            pass

    _cuda_avail = torch.cuda.is_available()
    _dbg(
        "torch.cuda diagnostic",
        {
            "torch_version": torch.__version__,
            "torch_cuda_version": str(torch.version.cuda),
            "cuda_is_available": _cuda_avail,
            "cudnn_available": torch.backends.cudnn.is_available() if hasattr(torch.backends, "cudnn") else "N/A",
            "cuda_device_count": torch.cuda.device_count() if _cuda_avail else 0,
            "cuda_device_name": torch.cuda.get_device_name(0) if _cuda_avail and torch.cuda.device_count() > 0 else "N/A",
            "NVIDIA_VISIBLE_DEVICES": os.environ.get("NVIDIA_VISIBLE_DEVICES", "NOT_SET"),
            "CUDA_VISIBLE_DEVICES": os.environ.get("CUDA_VISIBLE_DEVICES", "NOT_SET"),
        },
        "H1,H2,H3,H4",
    )
    # Check if libcuda.so is loadable
    _libcuda_path = _dcu.find_library("cuda")
    _libcuda_loadable = False
    try:
        if _libcuda_path:
            _dc.CDLL(_libcuda_path)
            _libcuda_loadable = True
        else:
            _dc.CDLL("libcuda.so.1")
            _libcuda_loadable = True
    except OSError as _e:
        _libcuda_err = str(_e)
    else:
        _libcuda_err = None
    _dbg(
        "libcuda check",
        {
            "find_library_cuda": _libcuda_path,
            "libcuda_loadable": _libcuda_loadable,
            "libcuda_error": _libcuda_err,
        },
        "H3,H5",
    )
    # Check nvidia-smi from inside container
    try:
        _nvsmi = _dsp.run(["nvidia-smi", "--query-gpu=name,driver_version,memory.total", "--format=csv,noheader"], capture_output=True, text=True, timeout=5)
        _dbg("nvidia-smi", {"stdout": _nvsmi.stdout.strip(), "stderr": _nvsmi.stderr.strip(), "returncode": _nvsmi.returncode}, "H2,H3")
    except Exception as _e:
        _dbg("nvidia-smi", {"error": str(_e)}, "H2,H3")
    # Check what CUDA libs exist
    try:
        _ldconfig = _dsp.run(["ldconfig", "-p"], capture_output=True, text=True, timeout=5)
        _cuda_libs = [_line.strip() for _line in _ldconfig.stdout.splitlines() if "cuda" in _line.lower() or "cublas" in _line.lower() or "cudnn" in _line.lower()]
        _dbg("cuda shared libs", {"libs": _cuda_libs[:20]}, "H5")
    except Exception as _e:
        _dbg("cuda shared libs", {"error": str(_e)}, "H5")
    # #endregion

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
