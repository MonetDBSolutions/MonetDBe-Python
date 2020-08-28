#!/usr/bin/env bash
set -e
set -v

pip3 install .
pycodestyle monetdbe tests

