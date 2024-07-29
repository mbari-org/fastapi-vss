# ================================================================
#  Docker image for fastapi-vss
#  ================================================================
FROM mbari/fastapi-vss:latest

# Install gcc and other build tools and libraries which are needed for numpy dependencies
RUN apk --no-cache add gcc g++ make blas-dev lapack-dev gfortran musl-dev git libffi-dev cmake

LABEL vendor="MBARI"
LABEL maintainer="dcline@mbari.org"
LABEL license="Apache License 2.0"

ARG GIT_VERSION=latest
ARG IMAGE_URI=mbari/fastapp-vss:${GIT_VERSION}

# Create a virtual environment for the application dependencies.
ENV VIRTUAL_ENV=/home/docker_user/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN if [ "$GIT_VERSION" != "latest" ]; then \
    git clone -b v${GIT_VERSION} --depth 1 https://github.com/mbari-org/fastapi-vss.git; \
    else \
    git clone --depth 1 https://github.com/mbari-org/fastapi-vss.git;\
    fi

# Clone the submodules and install the dependencies
RUN cd fastapi-vss && git submodule update --init --recursive && python -m pip3 install -e .

# run the FastAPI server
EXPOSE 80
ENTRYPOINT ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
