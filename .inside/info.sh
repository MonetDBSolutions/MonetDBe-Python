#!/bin/bash -ve

pip3 install .
python3 -c "from monetdbe.util import get_info; get_info()"

