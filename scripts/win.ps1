# notes on how to manually build on Windows, assuming all dependencies are installed

$MONETDBE_ROOT = "C:\Users\gijs\Code\MonetDBe-Python"
$MONETDB_ROOT = "C:\Users\gijs\Code\MonetDB"
$VCPKG_ROOT = "c:\build\vcpkg"
$PYTHON = "c:\python38\python.exe"

Set-Location $MONETDB_ROOT
mkdir build
Set-Location build

cmake -G "Visual Studio 16 2019" `
    -A x64 `
    -DCMAKE_TOOLCHAIN_FILE=c:\build\vcpkg\scripts\buildsystems\vcpkg.cmake `
    -DCMAKE_INSTALL_PREFIX=C:\monetdb `
    -DTESTING=OFF `
    -DCMAKE_BUILD_TYPE=Release `
    -DASSERT=OFF `
    -DODBC=false `
    -DPY3INTEGRATION=OFF `
    -DINT128=OFF  ..

cmake --build . --target ALL_BUILD -j 16  --config Release
cmake --build . --target INSTALL  --config Release


Set-Location $MONETDBE_ROOT
Remove-Item monetdbe\*.dll

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
Copy-Item $VCPKG_ROOT\installed\x64-windows\bin\bz2.dll monetdbe\.
Copy-Item $VCPKG_ROOT\installed\x64-windows\bin\libcurl.dll monetdbe\.

Remove-Item -Recurse -Force venv
Remove-Item -Recurse -Force .eggs
Remove-Item -Recurse -Force .pytest_cache
Remove-Item -Recurse -Force build
Remove-Item -Recurse -Force dist
Remove-Item -Recurse -Force monetdbe.egg-info
& $PYTHON -m venv venv

venv\Scripts\activate

pip install --upgrade pip wheel
python setup.py build_ext `
            --include-dirs=C:\monetdb\include `
            --library-dirs=C:\monetdb\lib


pip install -e .[test]