# Suraya

_A blend of Grafana and Marimo, with flavours of AMG and PMM._

## About

Grafana Suraya is a community distribution of Grafana, with batteries
included, similarly like AWS and Percona are doing it.

Pairing [Grafana] with reactive notebooks using [Jupyter] and [Marimo]
technologies optimally connects the Grafana and Python software ecosystems,
and provides a gateway from one to the other.

## Topics

**[Amazon Managed Grafana]** (AMG) provides scalable and secure data
visualization for your operational metrics, logs, and traces, as a fully
managed service developed in collaboration with Grafana Labs and Amazon
Web Services (AWS). It includes 40+ additional best-of-breed plugins from
the Grafana Marketplace.
On top of this curated set of baseline plugins, Suraya additionally includes
all 7 plugins of the [Volkov Labs Business Suite for Grafana].

**[CrateDB]** is a distributed and scalable SQL database for storing and
analyzing massive amounts of data in near real-time, even with complex
queries. It is PostgreSQL-compatible, and based on Lucene.

**[Grafana]**, traditionally like »Dashboard anything. Observe everything.«,
and still going strong, it makes you query, visualize, alert on, and
understand your data no matter where it’s stored. With Grafana, you can create,
explore, and share all of your data through beautiful, flexible dashboards,
on top of many high-quality database connectors.

**[Marimo]** is an open-source reactive notebook for Python — reproducible,
git-friendly, executable as a script, and shareable as an app.
Marimo notebooks are reproducible, extremely interactive, designed for
collaboration, and reactive, which means that when running a cell or
interacting with an UI element, Marimo will backtrack and update
all dependent cells and UI elements when needed. Contrary to Jupyter
Notebooks using the JSON format, Marimo notebooks are stored
as pure Python, executable as a script, and deployable as an app.

**[Percona Monitoring and Management]** (PMM) is an open source database
observability, monitoring, and management tool for use with MySQL, PostgreSQL,
MongoDB, and the servers on which they run, enabling to view node- to single-
query performance metrics for all of your databases in a single place.
The _Query Analytics_ subsystem quickly locates costly and slow-running queries
to address bottlenecks.
_Percona Advisors_ provide performance, security, and configuration
recommendations, and
_alerting and management_ features like backup, restore, and built-in open
source Private DBaaS complete the story.

**[PyViz]** enumerates the best open-source (OSS) Python data visualization tools in
different categories. Marimo provides the gateway to all of them.

## Usage

```shell
uv pip install suraya
python -m suraya.system.mk boot
```

```shell
open http://localhost:8080/
```

Credentials are: admin/grafana

Start Grafana Suraya with admin password `grafana`.
```shell
docker run --rm -it \
  --publish=3000:3000 \
  --env='GF_SECURITY_ADMIN_PASSWORD=grafana' \
  ghcr.io/daq-tools/grafana-suraya:latest
```

**Note:** This OCI image is not publicly available yet. However, it is easy
to build it on your workstation: Please consider following up at reading the
documentation about the [development sandbox][sandbox].

## Features

- **Batteries included:** A curated set of Grafana plugins provides the
  convenience of Amazon Managed Grafana (AMG) for the masses, with the
  additional freedom that it is easy to add your own, proprietary or not.

- **Developer friendly:** Fast, incremental OCI builds, also on pull requests,
  so you can ship development results fast, without even thinking about it.
  Short release cycles, and a friendly community with a happy-to-merge
  attitude, in order to ship early and often.

- **Releases:** Grafana Suraya is an OCI-based distribution, based on stable
  releases of Grafana OSS, and its nightly variants.

## What's inside

```shell
alias suraya='docker run --rm -it --entrypoint= ghcr.io/daq-tools/grafana-suraya:latest'
```

Display Grafana version.
```shell
suraya grafana --version
```

Display list of installed plugins.
```shell
suraya gf-plugins-list
```

```text
ae3e-plotly-panel @ 0.5.0
alexanderzobnin-zabbix-app @ 4.6.1
dlopes7-appdynamics-datasource @ 3.10.4
grafana-athena-datasource @ 3.0.0
grafana-bigquery-datasource @ 2.0.1
grafana-clickhouse-datasource @ 4.5.1
grafana-clock-panel @ 2.1.8
grafana-cloudflare-datasource @ 0.1.2-preview
grafana-databricks-datasource @ 1.10.4
grafana-datadog-datasource @ 3.12.4
grafana-dynatrace-datasource @ 3.21.4
grafana-github-datasource @ 2.0.1
grafana-gitlab-datasource @ 2.3.11
grafana-googlesheets-datasource @ 2.0.1
grafana-honeycomb-datasource @ 2.7.7
grafana-iot-sitewise-datasource @ 1.25.2
grafana-iot-twinmaker-app @ 2.0.0
grafana-jira-datasource @ 1.11.4
grafana-mongodb-datasource @ 1.22.8
grafana-newrelic-datasource @ 4.6.8
grafana-opensearch-datasource @ 2.22.3
grafana-oracle-datasource @ 2.10.4
grafana-redshift-datasource @ 1.20.0
grafana-salesforce-datasource @ 1.7.8
grafana-saphana-datasource @ 1.7.5
grafana-servicenow-datasource @ 2.12.14
grafana-snowflake-datasource @ 1.12.4
grafana-splunk-datasource @ 5.4.1
grafana-splunk-monitoring-datasource @ 1.7.10
grafana-timestream-datasource @ 2.9.13
grafana-wavefront-datasource @ 2.5.8
grafana-x-ray-datasource @ 2.13.1
marcusolsson-gantt-panel @ 0.8.1
marcusolsson-hourly-heatmap-panel @ 2.0.1
michaeldmoore-scatter-panel @ 1.2.0
moogsoft-aiops-app @ 9.0.0
netsage-sankey-panel @ 1.1.3
operato-windrose-panel @ 1.2.0
pixie-pixie-datasource @ 0.0.9
redis-datasource @ 2.2.0
simpod-json-datasource @ 0.6.6
volkovlabs-echarts-panel @ 6.5.0
volkovlabs-form-panel @ 5.0.0
volkovlabs-grapi-datasource @ 3.4.0
volkovlabs-image-panel @ 6.2.0
volkovlabs-rss-datasource @ 4.3.0
volkovlabs-table-panel @ 2.0.0
volkovlabs-variable-panel @ 3.6.0
```

Display number of installed plugins.
```shell
suraya gf-plugins-count
```
```
48
```

## Screenshots

[![Grafana Dashboard][grafana-small]][grafana-large]
[![Marimo NYC Rats][marimo-small]][marimo-large]


[Amazon Managed Grafana]: https://aws.amazon.com/grafana/
[AMG 2020]: https://aws.amazon.com/blogs/aws/announcing-amazon-managed-grafana-service-in-preview/
[AMG 2021a]: https://aws.amazon.com/blogs/mt/amazon-managed-service-for-grafana-amg-preview-updated-with-new-capabilities/
[AMG 2021b]: https://aws.amazon.com/blogs/aws/amazon-managed-grafana-is-now-generally-available-with-many-new-features/
[CrateDB]: https://en.wikipedia.org/wiki/CrateDB
[Grafana]: https://en.wikipedia.org/wiki/Grafana
[Grafana Image Renderer]: https://grafana.com/docs/grafana/latest/setup-grafana/image-rendering/
[grafana-large]: https://grafana.com/media/products/cloud/grafana/grafana-dashboard-english.png
[grafana-small]: https://grafana.com/media/products/cloud/grafana/grafana-dashboard-english.png?h=400
[Jupyter]: https://en.wikipedia.org/wiki/Jupyter
[Marimo]: https://marimo.io/
[marimo-large]: https://pbs.twimg.com/media/Gd_xn-iWgAAHFqY?format=jpg&name=large
[marimo-small]: https://pbs.twimg.com/media/Gd_xn-iWgAAHFqY?format=jpg&name=small
[Percona Monitoring and Management]: https://www.percona.com/software/database-tools/percona-monitoring-and-management
[PyViz]: https://pyviz.org/
[sandbox]: https://github.com/daq-tools/suraya/blob/main/notebooks/docs/sandbox.md
[Volkov Labs Business Suite for Grafana]: https://volkovlabs.io/
