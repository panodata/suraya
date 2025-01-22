# Build definition for Grafana Suraya, a clone of AMG.
#
# - https://grafana.com/docs/grafana/latest/setup-grafana/installation/docker/
# - https://github.com/grafana/grafana/blob/main/Dockerfile
# - https://github.com/grafana/grafana/blob/main/packaging/docker/custom/Dockerfile
# - https://docs.docker.com/build/building/multi-stage/
#
# For more verbose output, use:
# export BUILDKIT_PROGRESS=plain

# Define Grafana and Python versions.
ARG GRAFANA_VERSION="11.4.0"
ARG PYTHON_VERSION="3.13"

FROM python:${PYTHON_VERSION}-slim-bookworm AS plugins

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
    UV_SYSTEM_PYTHON=true

# Install prerequisites.
RUN apt-get update
RUN apt-get --yes install --no-install-recommends --no-install-suggests p7zip-full unzip

# Install `uv` package manager.
# https://docs.astral.sh/uv/guides/integration/docker/#installing-uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

ARG SOURCE_DIR=/src
ARG CACHE_DIR=/root/.cache
ARG SCRATCH_DIR=/tmp
ARG PLUGINS_DOWNLOAD_DIR=${CACHE_DIR}/plugins
ARG PLUGINS_INSTALL_DIR=/opt/grafana-plugins

ARG PLUGIN_MANIFEST_FILE=plugin-manifest.json
ARG PLUGIN_URLS_FILE=${SCRATCH_DIR}/plugin-urls.txt

# Populate staging area.
WORKDIR ${SOURCE_DIR}
COPY --from=plugins . .
COPY --from=module ${PLUGIN_MANIFEST_FILE} .

# Install Python package.
RUN ls -alF
RUN uv pip install --editable=.

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
    && uv run -m suraya.grafana.mk plugins-download "${PLUGIN_MANIFEST_FILE}" "${PLUGINS_DOWNLOAD_DIR}" \
    && echo "Plugins downloaded successfully" \
    && ls -alF ${PLUGINS_DOWNLOAD_DIR}/*.zip

# TODO: Fold this into Python lands as well.
RUN \
    --mount=type=cache,id=cache,target=${CACHE_DIR} \
    --mount=type=tmpfs,id=scratch,target=${SCRATCH_DIR} \
    true \
    && echo "Extracting plugins" \
    #&& zip ${PLUGINS_DOWNLOAD_DIR}/*.zip -d "${PLUGINS_INSTALL_DIR}" \
    && for plugin in ${PLUGINS_DOWNLOAD_DIR}/*.zip; do 7z x ${plugin} -o"${PLUGINS_INSTALL_DIR}/" | grep "Path"; done


# Derive from Grafana OSS.
FROM grafana/grafana-oss:${GRAFANA_VERSION}-ubuntu

# Switch from user `grafana` to `root`,
# in order to permit reconfiguring the image.
USER root

# Seed README.md into root folder.
COPY README.md /

# Configure paths for utility programs.
ARG GRAFANA_PLUGINS_LIST=/usr/local/bin/gf-plugins-list
ARG GRAFANA_PLUGINS_COUNT=/usr/local/bin/gf-plugins-count

# Install plugins.
RUN echo "Installing plugins"
COPY --from=plugins /opt/grafana-plugins "${GF_PATHS_PLUGINS}"
RUN \
    true \
    && chown -R grafana "${GF_PATHS_PLUGINS}" \
    && echo "Plugins installed successfully"

# Install utility programs.
RUN \
    true \
    && echo "#!/bin/sh\ngrafana cli plugins ls | grep -v 'installed plugins:' | sort" > "${GRAFANA_PLUGINS_LIST}" \
    && echo "#!/bin/sh\n${GRAFANA_PLUGINS_LIST} | wc -l" > "${GRAFANA_PLUGINS_COUNT}" \
    && chmod +x "${GRAFANA_PLUGINS_LIST}" \
    && chmod +x "${GRAFANA_PLUGINS_COUNT}"

# Enhance system settings.
RUN \
    true \
    && cp /root/.bashrc /root/.profile /home/grafana/ \
    && chown -R grafana /home/grafana

# Switch back to user `grafana` and original working directory,
# effectively locking down the image again.
USER grafana
WORKDIR $GF_PATHS_HOME

# Pre-flight checks.
RUN echo "List of installed plugins:"
RUN gf-plugins-list
RUN echo "Number of installed plugins:"
RUN gf-plugins-count

# Optionally, unset the `/run.sh` entrypoint, in order to easier invoke arbitrary commands.
# Otherwise, use `--entrypoint=` on the CLI to override it.
# ENTRYPOINT [ "" ]

# An example full DWIM command-line incantation using `--user=root --entrypoint=`.
# docker run --rm -it --user=root --entrypoint= grafana-suraya:dev bash
