#!/usr/bin/env python
"""
Marimo Suraya MK.
"""

# ruff: noqa: S603,S607
import importlib.resources
import logging
import os
import shlex
import subprocess
from textwrap import dedent

import click
import hishel
from pueblo import setup_logging


logger = logging.getLogger(__name__)


# HTTP client, with 1 hour of caching.
storage = hishel.FileStorage(ttl=3600)
http = hishel.CacheClient(storage=storage)

OCI_NAME_DEFAULT = "marimo-suraya:dev"


@click.group()
def cli():
    """
    Marimo Suraya Builder.
    """
    logger.info("Starting Marimo Suraya MK")


@cli.command()
@click.argument("image", type=str, default=OCI_NAME_DEFAULT)
def build(image: str):
    """
    Build OCI image.
    """
    os.environ["BUILDKIT_PROGRESS"] = "plain"
    os.environ["DOCKER_BUILDKIT"] = "1"

    folder = importlib.resources.files(__package__)
    subprocess.check_call(
        [
            "docker",
            "build",
            "--file",
            folder / "Dockerfile",
            "--build-context",
            f"module={folder}",
            "--tag",
            image,
            ".",
        ]
    )


@cli.command()
@click.argument("image", type=str, default=OCI_NAME_DEFAULT)
def run(image: str):
    """
    Run Marimo Suraya using OCI image.
    """
    command = dedent(f"""
    docker run --rm -it --name=marimo-suraya \
    --publish=4211:4211 \
    {image}
    """).replace("\n", "")
    subprocess.check_call(shlex.split(command))



if __name__ == "__main__":
    setup_logging()
    cli()
