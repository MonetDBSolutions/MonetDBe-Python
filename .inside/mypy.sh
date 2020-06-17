#!/bin/bash -ve

pip3 install -e .
mypy monetdbe tests
