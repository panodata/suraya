# Development Sandbox

A quick walkthrough how to work with the repository in development mode.

## Build

Build OCI image `grafana-nuraya:dev`.
```shell
git clone https://github.com/nurayadb/grafana-nuraya.git
cd grafana-nuraya
uv run mk.py build
```

Display list of installed plugins.
```shell
docker run --rm -it --entrypoint= grafana-nuraya:dev gf-plugins-list
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
alias nuraya='docker run --rm -it --entrypoint= grafana-nuraya:dev'
```

Display Grafana version.
```shell
nuraya grafana --version
```

Display list of installed plugins.
```shell
nuraya gf-plugins-list
```

Display number of installed plugins.
```shell
nuraya gf-plugins-count
```

If you want to change the ingredients, enter a root shell.
```shell
alias nuraya-root='docker run --rm -it --entrypoint= --user=root grafana-nuraya:dev'
nuraya-root bash
```
