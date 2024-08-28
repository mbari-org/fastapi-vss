# ================================================================
#  Docker image for fastapi-vss
#  ================================================================
FROM mbari/aidata:1.12.2

LABEL vendor="MBARI"
LABEL maintainer="dcline@mbari.org"
LABEL license="Apache License 2.0"

ARG GH_TOKEN
ARG GIT_VERSION=latest
ARG IMAGE_URI=mbari/aidata:${GIT_VERSION}

RUN apt-get update && apt-get install -y \
    software-properties-common \
    && apt-get update && apt-get install -y \
    git \
    python3.11 \
    python3.11-dev \
    python3.11-distutils \
    python3-pip \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

ENV APP_HOME=/app
WORKDIR ${APP_HOME}
ADD . ${APP_HOME}
ENV PYTHONPATH=${APP_HOME}/src:${APP_HOME}
WORKDIR $APP_HOME/src/submodules
RUN git clone https://${GH_TOKEN}@github.com/mbari-org/aidata
ENV HF_HOME=/tmp/transformers_cache

WORKDIR ${APP_HOME}
RUN python3.11 -m pip install -r src/requirements.txt

RUN chmod a+rwx -R /app

# run the FastAPI server
WORKDIR $APP_HOME/src/app
EXPOSE 80
ENTRYPOINT ["sh", "-c", "exec uvicorn main:app --host 0.0.0.0 --port 80 "]

