FROM quay.io/pypa/manylinux2014_x86_64
RUN yum install -y cmake3 
WORKDIR /tmp
RUN curl -O https://dev.monetdb.org/hg/MonetDB/archive/mbedded.tar.bz2
RUN tar jxvf mbedded.tar.bz2
RUN mkdir /tmp/MonetDB-mbedded/build
WORKDIR /tmp/MonetDB-mbedded/build
RUN cmake3 ..
RUN make -j 4
RUN make install

