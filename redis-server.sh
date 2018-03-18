#!/usr/bin/env bash

if [[ "$(docker ps -f name=redis_postprocess -q -f status=exited | wc -l)" != "0" ]]; then
 docker rm -f redis_phoner
fi


if [[ "$(docker ps -f name=redis_postprocess -q | wc -l)" == "0" ]]; then
 docker run -p 127.0.50.1:6379:6379 -d --name redis_postprocess redis
fi
