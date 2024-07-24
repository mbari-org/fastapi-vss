# ================================================================
#  Docker image for fastapi-tator
#  ================================================================
FROM ubuntu:20.04
LABEL vendor="MBARI"
LABEL maintainer="Danelle Cline dcline@mbari.org"
LABEL license="Apache License 2.0"

ARG IMAGE_URI=mbari/fastapi-tator

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


ARG APP_DIR=/app
WORKDIR $APP_DIR

## setup virtualenv
RUN pip install virtualenv
RUN virtualenv $APP_DIR/env -p python3.12
ENV VIRTUAL_ENV $APP_DIR/env
ENV PATH $APP_DIR/env/bin:$PATH

# install requirements and copy source
ENV PYTHONPATH=$APP_DIR/src
WORKDIR $APP_DIR/src/app
COPY ./src/requirements.txt $APP_DIR/src/requirements.txt
COPY ./src/app $APP_DIR/src/app
RUN pip install --no-cache-dir --upgrade -r $APP_DIR/src/requirements.txt

# set MBARI docker user and group id
ARG DOCKER_GID=136
ARG DOCKER_UID=582

RUN mkdir /sqlite_data

# Add a non-root user
RUN groupadd -f -r --gid ${DOCKER_GID} docker && \
    useradd -r --uid ${DOCKER_UID} -g docker docker_user && \
    chown -R docker_user:docker $APP_DIR

USER docker_user

# run the FastAPI server
EXPOSE 80
ENTRYPOINT ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
