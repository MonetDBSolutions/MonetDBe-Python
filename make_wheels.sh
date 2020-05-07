#!/bin/bash -ve

IMAGE=monetdbe

docker build --no-cache -t ${IMAGE} .
rm dist/*.whl
docker run -v `pwd`/dist:/dist:rw ${IMAGE} sh -c "cp /output/*.whl /dist"
