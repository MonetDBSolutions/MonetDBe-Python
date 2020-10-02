$BRANCH = 'Oct2020'


cmake -G "Visual Studio 16 2019" `
  -DCMAKE_TOOLCHAIN_FILE=$VCPKG_ROOT\scripts\buildsystems\vcpkg.cmake `
  -DCMAKE_INSTALL_PREFIX=C:\monetdb `
  -A x64 `
  -DTESTING=OFF `
  -DCMAKE_BUILD_TYPE=Release `
  -DASSERT=OFF `
  -DPY3INTEGRATION=OFF `
  -DODBC=false `
  -DINT128=OFF  ..


# install monetdb
cmake --build . --target ALL_BUILD --parallel 4
cmake --build . --target INSTALL

# collect vsckg dlls
Set-Location $GITHUB_WORKSPACE
Copy-Item C:\monetdb\bin\bat.dll monetdbe\.
Copy-Item C:\monetdb\bin\mapi.dll monetdbe\.
Copy-Item C:\monetdb\bin\monetdb5.dll monetdbe\.
Copy-Item C:\monetdb\bin\monetdbe.dll monetdbe\.
Copy-Item C:\monetdb\bin\monetdbsql.dll monetdbe\.
Copy-Item C:\monetdb\bin\stream.dll monetdbe\.

Copy-Item $VCPKG_ROOT\installed\x64-windows\bin\libcrypto-1_1-x64.dll monetdbe\.
Copy-Item $VCPKG_ROOT\installed\x64-windows\bin\libiconv.dll monetdbe\.
Copy-Item $VCPKG_ROOT\installed\x64-windows\bin\libxml2.dll monetdbe\.
Copy-Item $VCPKG_ROOT\installed\x64-windows\bin\pcre.dll monetdbe\.
Copy-Item $VCPKG_ROOT\installed\x64-windows\bin\zlib1.dll monetdbe\.
Copy-Item $VCPKG_ROOT\installed\x64-windows\bin\lzma.dll monetdbe\.
Copy-Item $VCPKG_ROOT\installed\x64-windows\bin\libcharset.dll monetdbe\.

Copy-Item $VCPKG_ROOT\installed\x64-windows\debug\bin\zlibd1.dll monetdbe\.
Copy-Item $VCPKG_ROOT\installed\x64-windows\debug\bin\bz2d.dll monetdbe\.
Copy-Item $VCPKG_ROOT\installed\x64-windows\debug\bin\libcurl-d.dll monetdbe\.
Copy-Item $VCPKG_ROOT\installed\x64-windows\debug\bin\lzmad.dll monetdbe\.


# build binary python stuff
C:\Python38\python.exe setup.py build_ext `
  --include-dirs=C:\monetdb\include `
  --library-dirs=C:\monetdb\lib

C:\Python38\python.exe -m pip install .[test]

# C:\Python38\Scripts\pytest.exe

# make wheel
C:\Python38\python.exe setup.py bdist_wheel

