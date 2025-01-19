#!/usr/bin/env sh

docker run --rm -it \
  --publish=3000:3000 \
  --env='GF_SECURITY_ADMIN_PASSWORD=admin' \
  grafana-nuraya:dev
