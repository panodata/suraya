#!/usr/bin/env sh

export BUILDKIT_PROGRESS=plain
docker build -t grafana-nuraya:dev .
