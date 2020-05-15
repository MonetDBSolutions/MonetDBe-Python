#!/bin/bash -ve

case "$1" in
    3.8)
        VERSION=38
        PLATFORM=""
        ;;
    3.7)
        VERSION=37
        PLATFORM="m"
        ;;
    3.6)
        VERSION=36
        PLATFORM="m"
        ;;
    *)
        echo "unsupposed argument"
        exit 1
esac

TARGET=cp${VERSION}-cp${VERSION}${PLATFORM}


/opt/python/${TARGET}/bin/pip install --upgrade pip pytest
/opt/python/${TARGET}/bin/pip install ".[full]"
/opt/python/${TARGET}/bin/py.test
                                                                    

