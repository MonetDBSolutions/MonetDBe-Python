#!/bin/bash -ve

IMAGE=monetdbe

#docker build -t ${IMAGE} .
rm build/*.whl
docker run -v `pwd`/build:/build:rw ${IMAGE} sh -c "cp /output/*.whl /build"
