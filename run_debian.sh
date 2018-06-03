#!/usr/bin/env bash
docker build . -f Dockerfile.debian -t cas-debian
docker run --rm -it -p 5000:5000 cas-debian