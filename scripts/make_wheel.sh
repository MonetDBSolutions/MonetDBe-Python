#!/usr/bin/env bash
#
# This should most likely be ran inside the cd docker container
#
set -e
set -v

WORKDIR=/tmp/
OUTPUT=dist/

case "$1" in
    3.12)
        VERSION=312
        PLATFORM=""
        ;;
    3.11)
        VERSION=311
        PLATFORM=""
        ;;
    3.10)
        VERSION=310
        PLATFORM=""
        ;;
    3.9)
        VERSION=39
        PLATFORM=""
        ;;
    3.8)
        VERSION=38
        PLATFORM=""
        ;;
    3.7)
        VERSION=37
        PLATFORM="m"
        ;;
    *)
        echo "unsupposed argument"
        exit 1
esac

ARCH=${2:-manylinux2014_x86_64}

TARGET=cp${VERSION}-cp${VERSION}${PLATFORM}

/opt/python/${TARGET}/bin/pip install --upgrade pip wheel build

/opt/python/${TARGET}/bin/pyproject-build -o ${WORKDIR}

auditwheel repair --plat ${ARCH} -w ${OUTPUT} ${WORKDIR}/*.whl
