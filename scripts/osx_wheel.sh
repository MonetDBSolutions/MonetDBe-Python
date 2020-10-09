#!/usr/bin/env bash
# Use this to make binary wheels for OSX
set -e
set -v

# install some requirements
brew install cmake bison openssl pyenv readline bzip2

# some settings and variables
PYTHONS=(3.6.11 3.7.8 3.8.5 3.9.0b5)
BRANCH=Oct2020

# no lets set some derivative variables
HERE="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
BUILD=${HERE}/../build
SRC=${BUILD}/MonetDB-${BRANCH}
PREFIX=${BUILD}/monetdb

# prepare for monetdb build
mkdir -p ${BUILD}
cd ${BUILD}

# download and install monetdb
if [ ! -f  ${BRANCH}.tar.bz2 ]; then
    curl -O -C - https://dev.monetdb.org/hg/MonetDB/archive/${BRANCH}.tar.bz2
fi

if [ ! -d ${SRC} ]; then
    tar jxvf ${BRANCH}.tar.bz2
fi

# compile the cargo
mkdir -p ${SRC}/build
cd ${SRC}/build
cmake .. \
  -DPY3INTEGRATION=OFF \
  -DBISON_EXECUTABLE=/usr/local/opt/bison/bin/bison \
  -DCMAKE_INSTALL_PREFIX=${PREFIX} \
  -DINT128=OFF \
  -DWITH_CRYPTO=OFF \
  -DCMAKE_BUILD_TYPE=Release \
  -DASSERT=OFF \
  -DRINTEGRATION=OFF
rm -rf ${PREFIX}
make -j5 install

# set some flags to find the monetdb libs
export CFLAGS="-I${PREFIX}/include -L${PREFIX}/lib"
export DYLD_LIBRARY_PATH=${PREFIX}/lib

# back to the origin
cd ${HERE}/..

# make the wheels
for p in "${PYTHONS[@]}"; do
    pyenv install -s ${p}
    ~/.pyenv/versions/${p}/bin/pip install wheel
    ~/.pyenv/versions/${p}/bin/python setup.py bdist_wheel
done

# make the wheels portable
~/.pyenv/versions/${PYTHONS[0]}/bin/pip install delocate
DYLD_LIBRARY_PATH=${PREFIX}/lib/ ~/.pyenv/versions/${PYTHONS[0]}/bin/delocate-wheel -v dist/*.whl
