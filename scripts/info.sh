#!/usr/bin/env bash
set -e
set -v

pip3 install .
python3 -c "from monetdbe.util import get_info; get_info()"

