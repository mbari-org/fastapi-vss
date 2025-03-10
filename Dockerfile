# ================================================================
#  Docker image for fastapi-vss
#  ================================================================
FROM mbari/aidata:1.41.9 AS base

LABEL vendor="MBARI"
LABEL maintainer="dcline@mbari.org"
LABEL license="Apache License 2.0"

ARG GIT_VERSION=latest
ARG IMAGE_URI=mbari/fastapi-vss:${GIT_VERSION}

ENV APP_HOME=/app
ENV PYTHONPATH=${APP_HOME}/src:${APP_HOME}

WORKDIR $APP_HOME
COPY . .
ENV HF_HOME=/tmp/transformers_cache

WORKDIR $APP_HOME
RUN python3 -m pip install -r src/requirements.txt && \
    python3 -m pip install https://github.com/redis/redis-py/archive/refs/tags/v5.0.9.zip

# run the FastAPI server
WORKDIR $APP_HOME/src/app
EXPOSE 80
ENTRYPOINT ["sh", "-c", "exec uvicorn main:app --host 0.0.0.0 --port 80 "]

