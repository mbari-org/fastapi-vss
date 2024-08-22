# ================================================================
#  Docker image for fastapi-vss
#  ================================================================
FROM ubuntu:20.04
LABEL vendor="MBARI"
LABEL maintainer="Danelle Cline dcline@mbari.org"
LABEL license="Apache License 2.0"

ARG PORT=80
ARG GH_TOKEN
ARG IMAGE_URI=mbari/fastapi-vss

ENV DEBIAN_FRONTEND=noninteractive
RUN apt update -y && apt install -y software-properties-common && \
    add-apt-repository -y ppa:deadsnakes/ppa &&  \
    apt-get install -y git \
	&& apt-get install -y build-essential \
	&& apt-get install -y python3.12 \
    && apt-get install -y python3-pip \
	&& apt-get install -y python3.12-dev \
	&& apt-get install -y python3.12-distutils \
	&& apt-get install -y libgl1-mesa-glx \
	&& apt-get install -y libglib2.0-0 \
	&& apt-get install -y libncurses6 \
    && apt-get install -y curl \
    && curl -sS https://bootstrap.pypa.io/get-pip.py | python3.12 \
    && python3.12 -m pip install --upgrade pip \
    && apt-get clean


WORKDIR $APP_DIR

## setup virtualenv
ENV APP_HOME=/app
RUN pip install virtualenv
RUN virtualenv $APP_DIR/env -p python3.12
ENV VIRTUAL_ENV $APP_HOME/env
ENV PATH $APP_HOME/env/bin:$PATH
ENV PYTHONPATH=${APP_HOME}/src:${APP_HOME}/src/submodules/aidata

WORKDIR $APP_HOME
COPY . .
WORKDIR $APP_HOME/src/submodules
RUN git clone https://${GH_TOKEN}@github.com/mbari-org/aidata
ENV HF_HOME=/tmp/transformers_cache

WORKDIR $APP_HOME
RUN python3 -m pip install --upgrade pip && \
    python3 -m pip install -r src/requirements.txt && \
    python3 -m pip install -r src/submodules/aidata/requirements.txt

# run the FastAPI server
WORKDIR $APP_HOME/src/app
EXPOSE ${PORT}
ENTRYPOINT ["sh", "-c", "exec uvicorn main:app --host 0.0.0.0 --port ${PORT} "]

