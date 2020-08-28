
:: in adminitrator powershell run

:: install chocolatey
@"%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe" `
 -NoProfile -InputFormat None -ExecutionPolicy Bypass `
 -Command "iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))" `
  && SET "PATH=%PATH%;%ALLUSERSPROFILE%\chocolatey\bin"
choco feature enable -n allowGlobalConfirmation

:: install deps
choco install winflexbison git
choco install python --version 3.6 --force
choco install python --version 3.7 --force
choco install python --version 3.8 --force
choco install python --version 3.9 --force

:: install visual studio 2017
cinst VisualStudio2017community --package-parameters `
  "--add Microsoft.VisualStudio.Workload.NativeDesktop --add microsoft.visualstudio.component.vc.cmake.project --add microsoft.visualstudio.component.vc.ATLMFC"
refreshenv
"c:\program files (x86)\microsoft visual studio\2017\community\common7\tools\vsdevcmd.bat"
"c:\Program Files (x86)\Microsoft Visual Studio\2017\Community\VC\Auxiliary\Build\vcvars64.bat"

:: install deps
mkdir c:\build
cd c:\build
git clone https://github.com/microsoft/vcpkg
cd vcpkg
bootstrap-vcpkg.bat -disableMetrics
set VCPKG_DEFAULT_TRIPLET=x64-windows
vcpkg install libiconv openssl bzip2 geos libxml2 pcre pcre2 zlib getopt --triplet x64-windows


:: get monetdb
cd c:\build
curl -O -C - https://dev.monetdb.org/hg/MonetDB/archive/oscar.tar.bz2
tar jxvf oscar.tar.bz2


:: compile monetdb
cd c:\build\MonetDB-oscar
cmake -G "Visual Studio 15 2017" `
  -DCMAKE_TOOLCHAIN_FILE=C:/build/vcpkg/scripts/buildsystems/vcpkg.cmake `
  -DCMAKE_INSTALL_PREFIX=C:/build/monetdb-installed -A x64 `
  -DTESTING=OFF -DCMAKE_BUILD_TYPE=Release -DASSERT=OFF `
  -DPY3INTEGRATION=OFF -DINT128=OFF  ..


:: install monetdb
cmake --build . --target ALL_BUILD --parallel 16
cmake --build . --target INSTALL

cd c\build\Monetdbe-python
cp c:\build\vcpkg\installed\x64-windows\bin\*.dll monetdbe\.
cp C:\build\monetdb-installed\bin\*.dll monetdbe\.


:: build binary python stuff
C:\Python36\python setup.py build_ext `
  --include-dirs=C:\build\monetdb-installed\include `
  --library-dirs=C:\build\monetdb-installed\lib


:: make wheel
C:\Python36\python setup.py bdist_wheel


:: and repeat for each python (3.6, 3.7, 3.8, 3.9)