#!/bin/bash -ve

IMAGE=monetdbe

#docker build -t ${IMAGE} .
rm dist/*.whl
docker run -v `pwd`/dist:/dist:rw ${IMAGE} sh -c "cp /output/*.whl /dist"
