#!/bin/bash
set -eu

docker container rm --force mtv_dl_web || true
# volume to cache the config and the mediathek database
docker volume create mtv_dl_config || true
docker build -t mtv_dl_web .
docker run -it \
    -p 8099:8099 \
    --name mtv_dl_web \
    --mount source=mtv_dl_config,target=/config \
    mtv_dl_web