# Development Sandbox

A quick walkthrough how to work with the repository in development mode.

## Build

Build OCI image `grafana-suraya:dev`.
```shell
git clone https://github.com/daq-tools/suraya.git
cd grafana-suraya
uv run mk.py build
```

Display list of installed plugins.
```shell
docker run --rm -it --entrypoint= grafana-suraya:dev gf-plugins-list
```

## Usage

Start Grafana with admin password `admin`.
```shell
uv run mk.py run
```

## Explore

In order to explore the image, nullify the entrypoint per `--entrypoint=`,
and invoke any command you want.

```shell
alias suraya='docker run --rm -it --entrypoint= grafana-suraya:dev'
```

Display Grafana version.
```shell
suraya grafana --version
```

Display list of installed plugins.
```shell
suraya gf-plugins-list
```

Display number of installed plugins.
```shell
suraya gf-plugins-count
```

If you want to change the ingredients, enter a root shell.
```shell
alias suraya-root='docker run --rm -it --entrypoint= --user=root grafana-suraya:dev'
suraya-root bash
```
