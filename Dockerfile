# ================================================================
#  Docker image for fastapi-vss
#  ================================================================
FROM python:3.11-slim

LABEL vendor="MBARI"
LABEL maintainer="dcline@mbari.org"
LABEL license="Apache License 2.0"

ARG GIT_VERSION=latest
ARG IMAGE_URI=mbari/fastapi-vss:${GIT_VERSION}

# curl needed for health-check
RUN apt-get update && apt-get install -y curl && apt-get clean

RUN python3 -m venv /venv

# Set environment variables
ENV PATH="/venv/bin:$PATH"
ENV APP_HOME=/app
ENV HF_HOME=/tmp/transformers_cache
ENV NO_ALBUMENTATIONS_UPDATE=1
ENV PYTHONPATH=${APP_HOME}/src:${APP_HOME}

WORKDIR $APP_HOME
COPY . .

WORKDIR $APP_HOME
RUN python3 -m pip install -r src/requirements.txt && \
    python3 -m pip install https://github.com/redis/redis-py/archive/refs/tags/v5.0.9.zip

# run the FastAPI server, but allow it to be overridden with a different command
WORKDIR $APP_HOME/src/app
EXPOSE 80
CMD ["sh", "-c", "exec uvicorn main:app --host 0.0.0.0 --port 80 "]
