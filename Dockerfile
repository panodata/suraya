# Build definition for Grafana Nuraya, a clone of AMG.
#
# - https://grafana.com/docs/grafana/latest/setup-grafana/installation/docker/
# - https://github.com/grafana/grafana/blob/main/Dockerfile
# - https://github.com/grafana/grafana/blob/main/packaging/docker/custom/Dockerfile
#
# For more verbose output, use:
# export BUILDKIT_PROGRESS=plain

# Define Grafana and Python versions.
ARG GRAFANA_VERSION="11.4.0"
ARG PYTHON_VERSION="3.13"

FROM python:${PYTHON_VERSION}-slim-bookworm AS plugins

ARG UV_VERSION="latest"

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
    UV_PYTHON=${PYTHON_VERSION} \
    UV_SYSTEM=true

# Install prerequisites.
RUN apt-get update
RUN apt-get --yes install --no-install-recommends --no-install-suggests git nano p7zip-full unzip wget

# Install `uv` package manager.
# https://docs.astral.sh/uv/guides/integration/docker/#installing-uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

ARG SOURCE_DIR=/src
ARG CACHE_DIR=/root/.cache
ARG SCRATCH_DIR=/tmp
ARG PLUGINS_DOWNLOAD_DIR=${CACHE_DIR}/plugins
ARG PLUGINS_INSTALL_DIR=/opt/grafana-plugins

ARG PLUGIN_MANIFEST_FILE=${SOURCE_DIR}/plugin-manifest.json
ARG PLUGIN_URLS_FILE=${SCRATCH_DIR}/plugin-urls.txt
ARG JQ_BIN_FILE=/usr/local/bin/jq

# Provide repository sources.
COPY . "${SOURCE_DIR}"

# Install Grafana plugins.
RUN echo "Installing plugins"
RUN \
    --mount=type=cache,id=cache,target=${CACHE_DIR} \
    --mount=type=tmpfs,id=scratch,target=${SCRATCH_DIR} \
    true \
    && mkdir -p "${PLUGINS_DOWNLOAD_DIR}" \
    && mkdir -p "${PLUGINS_INSTALL_DIR}" \
    #
    # Reset download directories.
    #&& rm -rf ${PLUGINS_DOWNLOAD_DIR} && exit 1 \
    #
    # Download plugins.
    && uv run /src/mk.py plugin-urls "${PLUGIN_MANIFEST_FILE}" > "${PLUGIN_URLS_FILE}" \
    && echo "Downloading plugins" \
    && wget --input-file="${PLUGIN_URLS_FILE}" --directory-prefix="${PLUGINS_DOWNLOAD_DIR}" \
        --content-disposition --no-clobber --quiet --show-progress --progress=bar:force:noscroll \
    && echo "Plugins downloaded successfully" \
    && ls -alF ${PLUGINS_DOWNLOAD_DIR}/*.zip \
    #
    && echo "Extracting plugins" \
    #&& zip ${PLUGINS_DOWNLOAD_DIR}/*.zip -d "${PLUGINS_INSTALL_DIR}" \
    && for plugin in ${PLUGINS_DOWNLOAD_DIR}/*.zip; do 7z x ${plugin} -o"${PLUGINS_INSTALL_DIR}/" | grep "Path"; done


# Derive from Grafana OSS.
FROM grafana/grafana-oss:${GRAFANA_VERSION}-ubuntu

# Switch from user `grafana` to `root`,
# in order to permit reconfiguring the image.
USER root

RUN echo "Installing plugins"
COPY --from=plugins /opt/grafana-plugins "${GF_PATHS_PLUGINS}"
RUN \
    true \
    && chown -R grafana "${GF_PATHS_PLUGINS}" \
    #
    && echo "Plugins installed successfully" \
    && grafana cli plugins ls \
    #
    && echo "Enhancing system settings" \
    && cp /root/.bashrc /root/.profile /home/grafana/ \
    && chown -R grafana /home/grafana

# Switch back to user `grafana`, effectively locking down the image again.
USER grafana

# Optionally, unset the `/run.sh` entrypoint.
# ENTRYPOINT [ "" ]

# Alternatively, use:
# docker run --rm -it --user=root --entrypoint=/bin/bash grafana-nuraya:dev
