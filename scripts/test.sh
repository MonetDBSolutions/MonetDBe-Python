#!/usr/bin/env bash
set -e
set -v

pip3 install pytest
pip3 install -e .
py.test -vv
                                                                    

