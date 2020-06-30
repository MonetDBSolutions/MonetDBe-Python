#!/bin/bash -ve

pip3 install .
mypy monetdbe tests
