#!/bin/bash -ve

IMAGE=monetdbe

docker build --no-cache -t ${IMAGE} .
rm -rf dist/*.whl
docker run -v `pwd`/dist:/dist:rw ${IMAGE} sh -c "cp /output/*.whl /dist"
