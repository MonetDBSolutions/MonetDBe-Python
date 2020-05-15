FROM quay.io/pypa/manylinux2014_x86_64

# install monetdb build dependencies
RUN yum install -y cmake3 

# download and extract monetdb
RUN mkdir /build && \
    cd /build && \
    curl -O https://dev.monetdb.org/hg/MonetDB/archive/mbedded.tar.bz2 && \
    tar jxvf mbedded.tar.bz2 && \
    mkdir /build/MonetDB-mbedded/build && \
    cd /build/MonetDB-mbedded/build && \
    cmake3 .. -DPython3_EXECUTABLE=/opt/python/cp38-cp38/bin/python && \
    make -j 4 && \
    make install && \
    cd / && \
    rm -rf /build

# add shared libraries to wheels
ENV LD_LIBRARY_PATH "${LD_LIBRARY_PATH}:/usr/local/lib64/monetdb5"

