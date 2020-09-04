$BRANCH = 'Oct2020'

# print the executed commands
Set-PSDebug -Trace 1


# get monetdb
Set-Location c:\
curl.exe -O https://dev.monetdb.org/hg/MonetDB/archive/$BRANCH.tar.bz2
unzip.exe $BRANCH.tar.bz2


# compile monetdb
Set-Location c:\MonetDB-$BRANCH
cmake -G "Visual Studio 16 2019" `
  -DCMAKE_TOOLCHAIN_FILE=$VCPKG_ROOT\scripts\buildsystems\vcpkg.cmake `
  -DCMAKE_INSTALL_PREFIX=C:\monetdb -A x64 `
  -DTESTING=OFF `
  -DCMAKE_BUILD_TYPE=Release `
  -DASSERT=OFF `
  -DPY3INTEGRATION=OFF `
  -DINT128=OFF  ..


# install monetdb
cmake --build . --target ALL_BUILD --parallel 4
cmake --build . --target INSTALL


# collect vsckg dlls
Set-Location $GITHUB_WORKSPACE
Copy-Item $VCPKG_ROOT\installed\x64-windows\bin\*.dll monetdbe\.
Copy-Item C:\monetdb\bin\*.dll monetdbe\.


# build binary python stuff
C:\Python38\python.exe setup.py build_ext `
  --include-dirs=C:\monetdb\include `
  --library-dirs=C:\monetdb\lib

C:\Python38\python.exe -m pip install --upgrade pip
C:\Python38\python.exe -m pip install pytest
C:\Python38\python.exe -m pip install -e .

# make wheel
C:\Python38\python.exe setup.py bdist_wheel

