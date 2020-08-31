$BRANCH = 'oscar'

# install choco deps
#choco install winflexbison git
#choco install python --version 3.6 --force
#choco install python --version 3.7 --force
#choco install python --version 3.8 --force
#choco install python --version 3.9 --force

# install deps
#cd C:\vcpkg
#bootstrap-vcpkg.bat -disableMetrics
#vcpkg install libiconv openssl bzip2 geos libxml2 pcre pcre2 zlib getopt --triplet x64-windows


# get monetdb
cd c:\
curl -O -C - https://dev.monetdb.org/hg/MonetDB/archive/$BRANCH.tar.bz2
tar jxvf $BRANCH.tar.bz2


# compile monetdb
cd c:\MonetDB-$BRANCH
cmake -G "Visual Studio 16 2019" `
  -DCMAKE_TOOLCHAIN_FILE=$VCPKG_ROOT/scripts/buildsystems/vcpkg.cmake `
  -DCMAKE_INSTALL_PREFIX=C:/monetdb -A x64 `
  -DTESTING=OFF `
  -DCMAKE_BUILD_TYPE=Release `
  -DASSERT=OFF `
  -DPY3INTEGRATION=OFF `
  -DINT128=OFF  ..


# install monetdb
cmake --build . --target ALL_BUILD --parallel 4
cmake --build . --target INSTALL

cd $GITHUB_WORKSPACE
cp $VCPKG_ROOT\installed\x64-windows\bin\*.dll monetdbe\.
cp C:\monetdb\bin\*.dll monetdbe\.


# build binary python stuff
C:\Python36\python setup.py build_ext `
  --include-dirs=C:\monetdb\include `
  --library-dirs=C:\monetdb\lib


# make wheel
C:\Python36\python setup.py bdist_wheel

