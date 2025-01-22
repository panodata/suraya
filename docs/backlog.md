# Backlog

## Iteration +1
- Composition/Infra: Provide Docker Compose file 
- Composition/HTTP: Grafana vs. marimo vs. Jupyter vs. API: `/g` vs. `/m` vs. `/j` vs. `/a`
- Composition/Persistence: `grafana.db`
- CI: Add software tests
- CI: Stage OCI builds to GHCR
- Release 0.0.0

## Iteration +2
- mk: Reading plugin manifest from TOML
- mk: Capability to use package name prefixes in plugin manifest,
  to get rid of custom code like adding `volkovlabs-` manually.
- mk: Real Python package
- OCI: Install tools from `grafana-toolbox`
- OCI/mk: Vendoring: base vs. cratedb-cockpit
- Documentation: Add synopsis about other subcommands than just
  `build` and `run`
- Documentation: Sphinx+RTD
- Documentation: What about installing fonts into Debian?
  See upstream docs.
- Documentation: Discriminate between datasource plugins and
  panel plugins, and enumerate them concisely.

## Iteration +3
- Grafana: Slightly adjust design/layout
  - Change logo
  - Add custom splash screen per dashboard
  - Add custom application
- OCI: Add metadata
- OCI: Testing & QA
- OCI: Nightly builds
- Integrate with grafana-image-renderer
- **Reporting:** [Grafana Image Renderer]
- JupyterLab
- Curvenote: https://github.com/curvenote/curvenote
- Grafana Scenes: https://github.com/grafana/scenes

## Done
- OCI: Multi-stage builds
- mk: Add `plugin-manifest.json`
- Dissolve `build.sh` and `run.sh`
- mk: Respect version numbers
- OCI/mk: Pythonify
- mk: More fluent API
- Naming things: Manifest `s/name/slug/`?
- OCI: Seed with README.md, README.html
- Naming things: Nuraya, Suraya, Naranja, Naraja
- Naming things: `s/Nuraya/Suraya/`?
- Refactoring: Make it a real package called `suraya`
