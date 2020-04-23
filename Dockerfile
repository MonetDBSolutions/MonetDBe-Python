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
RUN cmake3 ..
RUN make -j 4
RUN make install

# copy monetdbe into container, build wheels
ADD . /code
WORKDIR /code
RUN /opt/python/cp35-cp35m/bin/python ./setup.py bdist_wheel -d .
RUN /opt/python/cp36-cp36m/bin/python ./setup.py bdist_wheel -d .
RUN /opt/python/cp37-cp37m/bin/python ./setup.py bdist_wheel -d .
RUN /opt/python/cp38-cp38/bin/python ./setup.py bdist_wheel -d .

# add shared libraries to wheels
RUN auditwheel repair --plat manylinux2014_x86_64 -w /output *.whl
