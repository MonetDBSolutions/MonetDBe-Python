#!/bin/bash -ve

pip3 install -e .
pycodestyle monetdbe tests

