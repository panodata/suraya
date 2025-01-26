# Boot Suraya from Compose recipe.
# https://gabrieldemarmiesse.github.io/python-on-whales/sub-commands/compose/
import logging
from importlib import resources
from importlib.resources import files
from pathlib import Path

import click
from pueblo import setup_logging
from python_on_whales import DockerClient

logger = logging.getLogger(__name__)


class Suraya:
    """
    """
    def __init__(self):
        with resources.as_file(resources.files(__package__) / "compose.yaml") as compose_file:
            self.docker = DockerClient(compose_files=[compose_file])
    def boot(self):
        self.docker.compose.up()


@click.group()
def cli():
    """
    Suraya CLI.
    """
    logger.info("Starting Suraya")


@cli.command()
def boot():
    """
    Start Suraya.
    """
    Suraya().boot()


if __name__ == "__main__":
    setup_logging()
    cli()
