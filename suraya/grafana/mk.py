#!/usr/bin/env python
"""
Grafana Suraya MK.
"""

# ruff: noqa: S603,S607
import importlib.resources
import json
import logging
import os
import shlex
import subprocess
import sys
import typing as t
import urllib.parse
from pathlib import Path
from textwrap import dedent

import attrs
import click
import hishel
import httpx
from munch import Munch
from pueblo import setup_logging
from pypdl import pypdl


logger = logging.getLogger(__name__)


# HTTP client, with 1 hour of caching.
storage = hishel.FileStorage(ttl=3600)
http = hishel.CacheClient(storage=storage)

OCI_NAME_DEFAULT = "grafana-suraya:dev"


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
        # TODO: Limit number by `[:3]` here.
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
                    self.items.append(Plugin(slug=item["slug"], version=item["version"]))
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
                f"slug={slug}, version={version}, prefix={prefix}"
            )
        return self

    def to_manifest(self):
        data = {
            "comment": "Plugins for Amazon Managed Grafana (AMG)",
            "plugins": [
                {"slug": plugin.slug, "version": plugin.version} for plugin in self.items
            ],
        }
        return json.dumps(data, indent=2)


def get_plugins_standard(path: Path) -> PluginList:
    """
    Get standard set of plugins, mostly AMG plus Volkov Labs.
    """
    plugins = PluginList()
    plugins.add_manifest(path).add_package(prefix="volkovlabs-")
    return plugins


@click.group()
def cli():
    """
    Grafana Suraya Builder.
    """
    logger.info("Starting Grafana Suraya MK")


@cli.command()
@click.argument("manifest", type=click.Path(exists=True, path_type=Path))
def update_manifest(manifest: Path):
    """
    Update the plugin manifest to use the most recent version of each plugin.
    """
    logger.info(f"BOM manifest path: {manifest}")
    plugins = get_plugins_standard(manifest)
    for plugin in plugins.items:
        plugin.version = plugins._catalog.find_plugin(plugin.slug).version
    print(plugins.to_manifest())  # noqa: T201


@cli.command()
@click.argument("path", type=click.Path(exists=True, path_type=Path))
def plugin_urls(path: Path):
    """
    Convert plugin manifests to list of URLs.
    """
    logger.info(f"Using manifest path: {path}")
    plugins = get_plugins_standard(path)
    print("\n".join(plugins.package_urls), file=sys.stdout)  # noqa: T201


@cli.command()
@click.argument("manifest", type=click.Path(exists=True, path_type=Path))
@click.argument("target", type=click.Path(exists=True, path_type=Path))
def plugins_download(manifest: Path, target: Path):
    """
    Download plugins by list of URLs.
    """
    logger.info(f"BOM manifest path: {manifest}")
    plugins = get_plugins_standard(manifest)
    acquire(plugins.package_urls, target)


def acquire(urls: t.List[str], target: Path):
    """
    Download and extract list of plugins from a list of URLs into a target folder.
    """

    def get_filename(url: str):
        """
        Only because pypdl does not respect the *redirected* download filename.
        """
        response = http.get(url)
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as ex:
            if not str(ex).startswith("Redirect response"):
                logger.error(f"Request failed: {ex}")
                # TODO: raise or continue?
                raise
        return Path(urllib.parse.urlsplit(http.get(url).headers["location"]).path).name

    # Build task list for pypdl downloader.
    tasks = []
    for url in urls:
        filename = get_filename(url)
        task = {"url": url, "file_path": str(target / filename)}
        tasks.append(task)

    # Invoke pypdl downloader.
    dl = pypdl.Pypdl(max_concurrent=3, allow_reuse=True)
    results = dl.start(
        tasks=tasks,
        multisegment=False,
        overwrite=False,
        display=True,
        block=True,
        retries=3,
        clear_terminal=False,
    )

    # Display download results.
    for result in results:
        if isinstance(result, tuple):
            url, result = result
            logger.info(f"Downloaded {url}")
        logger.info(f"Download succeeded: {result.path}")

    dl.stop()
    dl.shutdown()


@cli.command()
@click.argument("path", type=click.Path(exists=True, path_type=Path))
@click.pass_context
def plugins_install(ctx, path: Path):
    """
    Install list of plugins using Grafana CLI.
    """
    logger.info(f"Using download BOM path: {path}")
    plugins = get_plugins_standard(path)
    for plugin in plugins.items:
        ctx.invoke(plugin_install, slug=plugin.slug, version=plugin.version)


@cli.command()
@click.argument("slug", type=str, required=True)
@click.argument("version", type=str, required=False)
def plugin_install(slug: str, version: str):
    """
    Install plugin using Grafana CLI.
    """
    logger.info(f"Installing plugin: {slug}/{version}")
    command = f"grafana cli plugins install {slug} {version}"
    subprocess.check_call(shlex.split(command))


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
@click.argument("admin-password", type=str, default="admin")
def run(image: str, admin_password: str):
    """
    Run Grafana using OCI image.
    """
    command = dedent(f"""
    docker run --rm -it --name=grafana-suraya \
    --publish=3000:3000 \
    --env='GF_SECURITY_ADMIN_PASSWORD={admin_password}' \
    {image}
    """).replace("\n", "")
    subprocess.check_call(shlex.split(command))


if __name__ == "__main__":
    setup_logging()
    cli()
