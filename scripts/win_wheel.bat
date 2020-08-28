
:: as adminitrator run
@"%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe" `
 -NoProfile -InputFormat None -ExecutionPolicy Bypass `
 -Command "iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))" `
  && SET "PATH=%PATH%;%ALLUSERSPROFILE%\chocolatey\bin"
choco feature enable -n allowGlobalConfirmation
choco install winflexbison git
cinst VisualStudio2017community --package-parameters `
  "--add Microsoft.VisualStudio.Workload.NativeDesktop --add microsoft.visualstudio.component.vc.cmake.project --add microsoft.visualstudio.component.vc.ATLMFC"
refreshenv


:: install deps
mkdir c:\build
cd c:\build
git clone https://github.com/microsoft/vcpkg
cd vcpkg
bootstrap-vcpkg.bat -disableMetrics
:: vcpkg integrate install
:: needed for 64 bits (with the available python being 64 bit this is needed)
set VCPKG_DEFAULT_TRIPLET=x64-windows
vcpkg install libiconv openssl bzip2 geos libxml2 pcre pcre2 zlib getopt


:: get monetdb
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


:: build binary python stuff
cd c:\build\monetdbe-Python
python setup.py build_ext `
  --include-dirs=C:\build\monetdb-installed\include `
  --library-dirs=C:\build\monetdb-installed\bin


:: make wheel
python setup.py bdist_wheel