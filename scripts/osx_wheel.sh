#!/usr/bin/env bash
# Use this to make binary wheels for OSX
set -e
set -v


# this script uses homebrew, install with:
#
#   $ /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install.sh)"
#
# then install some requirements:
#
brew install cmake bison openssl pyenv readline bzip2


# some settings and variables
PYTHONS=(3.6.12 3.7.9 3.8.5)
BRANCH=oscar

# no lets set some derivative variables
HERE="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
BUILD=${HERE}/build
SRC=${BUILD}/MonetDB-${BRANCH}
PREFIX=${BUILD}/monetdb

# make sure the pythons are installed
for p in "${PYTHONS[@]}"; do
    pyenv install -s ${p}
done

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
cmake .. -DPY3INTEGRATION=OFF -DBISON_EXECUTABLE=/usr/local/opt/bison/bin/bison -DCMAKE_INSTALL_PREFIX=${PREFIX} -DINT128=OFF -DWITH_CRYPTO=OFF -DCMAKE_BUILD_TYPE=Release -DASSERT=OFF
rm -rf ${PREFIX}
make -j5 install

# set some flags to find the monetdb libs
export CFLAGS="-I${PREFIX}/include -L${PREFIX}/lib"
export DYLD_LIBRARY_PATH=${PREFIX}/lib

# back to the origin
cd ${HERE}

# make the wheels
for p in ${PYTHONS[@]}; do
    ~/.pyenv/versions/${p}/bin/pip install wheel
    ~/.pyenv/versions/${p}/bin/python setup.py bdist_wheel
done

# make the wheels portable
~/.pyenv/versions/${PYTHONS[0]}/bin/pip install delocate
DYLD_LIBRARY_PATH=${PREFIX}/lib/ ~/.pyenv/versions/${PYTHONS[0]}/bin/delocate-wheel -v dist/*.whl