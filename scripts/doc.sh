#!/usr/bin/env bash
set -e
set -v

pip3 install --upgrade pip
pip3 install sphinx>=3.1.1 sphinx_rtd_theme numpy pandas
pip3 install -r doc/requirements.txt

cd doc
make html