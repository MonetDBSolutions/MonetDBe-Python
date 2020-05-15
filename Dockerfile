FROM quay.io/pypa/manylinux2014_x86_64

# install monetdb build dependencies
RUN yum install -y cmake3 

# download and extract monetdb
WORKDIR /tmp
RUN curl -O https://dev.monetdb.org/hg/MonetDB/archive/mbedded.tar.bz2
RUN tar jxvf mbedded.tar.bz2

# build and install monetdb
RUN mkdir /tmp/MonetDB-mbedded/build
WORKDIR /tmp/MonetDB-mbedded/build
RUN cmake3 .. -DPython3_EXECUTABLE=/opt/python/cp38-cp38/bin/python
RUN make -j 4
RUN make install

# add shared libraries to wheels
ENV LD_LIBRARY_PATH "${LD_LIBRARY_PATH}:/usr/local/lib64/monetdb5"

