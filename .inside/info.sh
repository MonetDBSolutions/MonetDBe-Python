#!/bin/bash -ve

pip3 install -e .
python3 -c "from monetdbe.util import get_info; get_info()"

