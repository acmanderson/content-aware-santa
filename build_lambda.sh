#!/usr/bin/env bash
set -e
docker build . -t cas-lambda
id=$(docker create cas-lambda)
docker cp $id:/var/task/build .
docker rm -v $id