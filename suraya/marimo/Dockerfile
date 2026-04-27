# Build definition for Marimo Suraya.

FROM python:3.14-slim-bookworm

ENV \
    #
    # Configure operating system.
    DEBIAN_FRONTEND=noninteractive \
    TERM=linux \
    #
    # Configure `pip` package manager.
    PIP_ROOT_USER_ACTION=ignore \
    #
    # Configure `uv` package manager.
    UV_COMPILE_BYTECODE=true \
    UV_LINK_MODE=copy \
    UV_SYSTEM_PYTHON=true

# Install `uv` package manager.
# https://docs.astral.sh/uv/guides/integration/docker/#installing-uv
COPY --from=ghcr.io/astral-sh/uv:0.11.8 /uv /uvx /usr/local/bin/

# Define a few directories.
ARG SOURCE_DIR=/src
ARG CACHE_DIR=/root/.cache

# Populate staging area.
COPY . ${SOURCE_DIR}

# Install Python package.
RUN \
    --mount=type=cache,id=cache,target=${CACHE_DIR} \
    true \
    && uv pip install --editable='/src[web]'

# Run Marimo Suraya.
ENTRYPOINT [ "uv", "run", "-m", "suraya.marimo.serve" ]
