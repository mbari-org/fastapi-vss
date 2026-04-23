# ================================================================
#  Docker image for fastapi-vss (multi-stage for smaller image)
# ================================================================
FROM python:3.11-slim AS builder

ARG GIT_VERSION=latest
ARG IMAGE_URI=mbari/fastapi-vss:${GIT_VERSION}

RUN python3 -m venv /venv
ENV PATH="/venv/bin:$PATH"

WORKDIR /app
COPY src/requirements.txt src/requirements.txt
RUN pip install --no-cache-dir -r src/requirements.txt && \
    pip install --no-cache-dir https://github.com/redis/redis-py/archive/refs/tags/v5.0.9.zip

# -----------------------------------------------------------------------------
FROM python:3.11-slim

LABEL vendor="MBARI"
LABEL maintainer="dcline@mbari.org"
LABEL license="Apache License 2.0"

ARG UID=1001
ARG GID=1001

# curl needed for health-check; clean apt in same layer to avoid bloating
RUN apt-get update && apt-get install -y --no-install-recommends curl && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

RUN groupadd --gid ${GID} appuser && \
    useradd --uid ${UID} --gid ${GID} --no-create-home appuser

ENV PATH="/venv/bin:$PATH"
ENV APP_HOME=/app
ENV HF_HOME=/tmp/transformers_cache
ENV NO_ALBUMENTATIONS_UPDATE=1
ENV PYTHONPATH=${APP_HOME}/src:${APP_HOME}
ENV IN_DOCKER=1

WORKDIR $APP_HOME
COPY --from=builder /venv /venv
COPY . .

RUN chown -R appuser:appuser /app /venv

USER ${UID}:${GID}

EXPOSE 80
WORKDIR $APP_HOME/src/app
CMD ["sh", "-c", "exec uvicorn main:app --host 0.0.0.0 --port 80 --ws-max-size 10485760"]
