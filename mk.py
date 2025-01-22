#!/usr/bin/env python
"""
## About
Build Grafana Nuraya.

## Synopsis
```shell
uv run mk.py --version nightly
```
"""

# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "attrs",
#     "click<9",
#     "hishel<0.2",
#     "munch<5",
# ]
# ///
import logging
import os
import shlex
import subprocess
import sys
import typing as t
from pathlib import Path
from textwrap import dedent

import attrs
import click
import hishel
from munch import Munch

log_format = "%(asctime)-15s [%(name)-16s] %(levelname)-8s: %(message)s"
logging.basicConfig(format=log_format, level=logging.INFO, stream=sys.stderr)

logger = logging.getLogger(__name__)


# HTTP client, with 1 hour of caching.
storage = hishel.FileStorage(ttl=3600)
http = hishel.CacheClient(storage=storage)

OCI_NAME_DEFAULT = "grafana-nuraya:dev"


@attrs.define()
class Plugin:
    """
    Manage minimal plugin information.
    """

    slug: str
    version: str


@attrs.define()
class GrafanaPluginInfo(Plugin):
    """
    Manage extended plugin information.
    """

    homepage_url: str
    repository_url: str
    package_url: str


class GrafanaPluginCatalog:
    """
    Manage the Grafana plugin catalog.
    """

    URL = "https://grafana.com/api/plugins"

    def __init__(self):
        self.data = Munch.fromDict(http.get(self.URL).json())

    def items(self) -> t.Iterator[Munch]:
        for item in self.data["items"]:
            yield item

    def i2p(self, item: Munch):
        try:
            return self.get_package_info(item)
        except ValueError as ex:
            logger.warning(f"Skipping {item.slug}: {ex}")

    def find_plugin(self, slug: str):
        # TODO: Optimize access by indexing by slug.
        for item in self.items():
            if item.slug == slug:
                return self.i2p(item)
        raise ValueError(f"Plugin {slug} not found")

    def get_plugins_by_prefix(self, prefix: str):
        # TODO: Optimize access by indexing by slug.
        for item in self.items():
            if item.slug.startswith(prefix):
                if value := self.i2p(item):
                    yield value

    def get_package_info(self, item: Munch):
        """
        Get plugin and package information.
        """
        # TODO: Select specific platform based on user choice or parent platform.
        candidates = ["linux-amd64", "any"]
        for candidate in candidates:
            if candidate in item.packages:
                return GrafanaPluginInfo(
                    slug=item.slug,
                    version=item.version,
                    homepage_url=f"https://grafana.com/grafana{item.links[0].href}",
                    repository_url=self.get_repository_url(item.url, item.slug),
                    package_url=f"https://grafana.com{item.packages[candidate].downloadUrl}",
                )
        raise ValueError(f"Package not found or unknown package type: {item.slug}")

    def get_repository_url(self, url: str, slug: str) -> t.Union[str, None]:
        if url == "https://github.com/grafana/plugins-private":
            return None
        if url:
            return url
        if "volkovlabs" in slug:
            return f"https://github.com/VolkovLabs/{slug}"
        return None


@attrs.define()
class PluginList:
    """
    Manage a list of plugin items.
    """

    tpl = "https://grafana.com/api/plugins/{name}/versions/{version}/download?os={os}&arch={arch}"

    items: t.List[Plugin] = attrs.field(default=[])
    _catalog: "GrafanaPluginCatalog" = attrs.field(factory=GrafanaPluginCatalog)

    @property
    def package_urls(self) -> t.List[str]:
        urls = []
        for item in self.items:
            if item.slug and item.version:
                url = self.tpl.format(
                    name=item.slug, version=item.version, os="linux", arch="amd64"
                )
            elif item.slug:
                info = self._catalog.find_plugin(slug=item.slug)
                if info is None:
                    logger.error(
                        f"Plugin does not exist in Grafana "
                        f"plugin catalog, skipping: {item.slug}"
                    )
                    continue
                url = info.package_url
            else:
                raise KeyError(f"Plugin not found: {item.slug}")
            urls.append(url)
        return urls

    def add_manifest(self, path: Path):
        if path.suffix == ".json":
            with open(path) as f:
                data = Munch.fromJSON(f.read())
            if "plugins" in data:
                for item in data["plugins"]:
                    self.items.append(Plugin(slug=item["name"], version=item["version"]))
            else:
                raise NotImplementedError("Manifest file format not supported")

        elif path.suffix == ".toml":
            raise NotImplementedError(
                "Reading plugin manifests from TOML not implemented yet"
            )

        else:
            raise click.FileError(str(path), f"Unsupported file extension: {path.suffix}")
        return self

    def add_package(self, slug: str = None, version: str = None, prefix: str = None):
        if slug and version:
            self.items.append(Plugin(slug=slug, version=version))
        elif prefix:
            for plugin in self._catalog.get_plugins_by_prefix(prefix):
                self.items.append(Plugin(slug=plugin.slug, version=plugin.version))
        else:
            raise KeyError(
                f"Plugin not found or incomplete information: "
                f"name={slug}, version={version}, prefix={prefix}"
            )
        return self


@click.group()
def cli():
    """
    Grafana Nuraya Builder.
    """
    logger.info("Starting Grafana Nuraya MK")


@cli.command()
@click.argument("path", type=click.Path(exists=True, path_type=Path))
def plugin_urls(path: Path):
    """
    Convert plugin manifests to list of URLs.
    """
    logger.info(f"Using manifest path: {path}")

    plugins = PluginList()
    plugins.add_manifest(path).add_package(prefix="volkovlabs-")

    print("\n".join(plugins.package_urls), file=sys.stdout)


@cli.command()
@click.argument("image", type=str, default=OCI_NAME_DEFAULT)
def build(image: str):
    """
    Build OCI image.
    """
    os.environ["BUILDKIT_PROGRESS"] = "plain"
    os.environ["DOCKER_BUILDKIT"] = "1"

    subprocess.check_call(["docker", "build", "-t", image, "."])


@cli.command()
@click.argument("image", type=str, default=OCI_NAME_DEFAULT)
@click.argument("admin-password", type=str, default="admin")
def run(image: str, admin_password: str):
    """
    Run Grafana using OCI image.
    """
    command = dedent(f"""
    docker run --rm -it --name=grafana-nuraya \
    --publish=3000:3000 \
    --env='GF_SECURITY_ADMIN_PASSWORD={admin_password}' \
    {image}
    """).replace("\n", "")
    subprocess.check_call(shlex.split(command))


if __name__ == "__main__":
    cli()
