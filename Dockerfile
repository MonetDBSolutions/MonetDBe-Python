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


# copy monetdbe into container, build wheels
ADD . /code
WORKDIR /code

# make binary wheels
RUN /opt/python/cp36-cp36m/bin/python ./setup.py bdist_wheel -d .
RUN /opt/python/cp37-cp37m/bin/python ./setup.py bdist_wheel -d .
RUN /opt/python/cp38-cp38/bin/python ./setup.py bdist_wheel -d .

# repair binary wheels
RUN auditwheel repair --plat manylinux2014_x86_64 -w /output monetdbe-*-cp36-cp36m-linux_x86_64.whl
RUN auditwheel repair --plat manylinux2014_x86_64 -w /output monetdbe-*-cp37-cp37m-linux_x86_64.whl
RUN auditwheel repair --plat manylinux2014_x86_64 -w /output monetdbe-*-cp38-cp38-linux_x86_64.whl

# run the test suite
#RUN /opt/python/cp38-cp38/bin/pip install --upgrade pip pytest
#RUN /opt/python/cp38-cp38/bin/pip install ".[full]"
#RUN /opt/python/cp38-cp38/bin/py.test

