
GITHUB_WORKSPACE=/build
DOCKER_IMAGE= monetdb/dev-builds:Oct2020

TEST_IMAGE = monetdb/dev-builds:Oct2020
WHEEL_IMAGE = monetdb/dev-builds:Oct2020_manylinux 


all: test

venv/:
	python3 -m venv venv
	venv/bin/pip install --upgrade pip wheel build setuptools

venv/bin/pytest: venv/
	venv/bin/pip install -e ".[test]"
	touch venv/bin/pytest

setup: venv/bin/pytest

build: venv/bin/pytest
	venv/bin/pyproject-build

test: venv/bin/pytest
	venv/bin/pytest

docker-wheels:
	docker run -v `pwd`:$(GITHUB_WORKSPACE) ${WHEEL_IMAGE} sh -c "cd $(GITHUB_WORKSPACE); scripts/make_wheel.sh 3.6"
	docker run -v `pwd`:$(GITHUB_WORKSPACE) ${WHEEL_IMAGE} sh -c "cd $(GITHUB_WORKSPACE); scripts/make_wheel.sh 3.7"
	docker run -v `pwd`:$(GITHUB_WORKSPACE) ${WHEEL_IMAGE} sh -c "cd $(GITHUB_WORKSPACE); scripts/make_wheel.sh 3.8"
	docker run -v `pwd`:$(GITHUB_WORKSPACE) ${WHEEL_IMAGE} sh -c "cd $(GITHUB_WORKSPACE); scripts/make_wheel.sh 3.9"

docker-test:
	docker run -ti -v `pwd`:$(GITHUB_WORKSPACE) ${TEST_IMAGE} sh -c "cd $(GITHUB_WORKSPACE); scripts/test.sh"

docker-mypy:
	docker run -v `pwd`:$(GITHUB_WORKSPACE) ${TEST_IMAGE} sh -c "cd $(GITHUB_WORKSPACE); scripts/mypy.sh"

docker-pycodestyle:
	docker run -v `pwd`:$(GITHUB_WORKSPACE) ${TEST_IMAGE} sh -c "cd $(GITHUB_WORKSPACE); scripts/pycodestyle.sh"

docker-info:
	docker run -v `pwd`:$(GITHUB_WORKSPACE) ${TEST_IMAGE} sh -c "cd $(GITHUB_WORKSPACE); scripts/info.sh"

docker-doc:
	docker run -v `pwd`:$(GITHUB_WORKSPACE) ${TEST_IMAGE} sh -c "cd $(GITHUB_WORKSPACE); scripts/doc.sh"

dockers: docker-wheels docker-test docker-mypy docker-pycodestyle docker-doc

clean: venv/
	venv/bin/python3 setup.py clean
	rm -rf build dist *.egg-info .eggs monetdbe/*.so monetdbe/*.dylib .*_cache venv/
	rm monetdbe/_cffi/branch.py
	find . -name __pycache__ | xargs rm -rf

venv/bin/mypy: venv/
	venv/bin/pip install mypy
	touch venv/bin/mypy

venv/bin/pycodestyle: venv/
	venv/bin/pip install pycodestyle
	touch venv/bin/pycodestyle

mypy: venv/bin/mypy
	venv/bin/mypy --show-error-codes monetdbe tests

pycodestyle: venv/bin/pycodestyle
	venv/bin/pycodestyle monetdbe tests

venv/bin/jupyter-notebook: venv/
	venv/bin/pip install notebook
	touch venv/bin/jupyter-notebook

notebook: venv/bin/jupyter-notebook
	venv/bin/jupyter-notebook

venv/bin/delocate-wheel: venv/
	venv/bin/pip install delocate
	touch venv/bin/delocate-wheel

delocate: venv/bin/delocate-wheel
	venv/bin/delocate-wheel -v dist/*.whl

venv/bin/twine: venv/
	venv/bin/pip install twine
	touch venv/bin/twine

twine: venv/bin/twine
	venv/bin/twine upload dist/*.whl dist/*.tar.gz

info: setup
	venv/bin/python -c "from monetdbe._cffi.util import print_info; print_info()"

venv/bin/ipython: venv/
	venv/bin/pip install ipython

ipython: venv/bin/ipython
	venv/bin/ipython

venv38/:
	/opt/homebrew/Cellar/python@3.8/3.8.*/bin/python3.8 -m venv venv38

venv39/:
	/opt/homebrew/Cellar/python@3.9/3.9.*/bin/python3.9 -m venv venv39

venv310/:
	/opt/homebrew/Cellar/python@3.10/3.10.*/bin/python3.10 -m venv venv310

osx-m1-all-wheels: venv38/ venv39/ venv310/
	venv38/bin/pip install --upgrade pip wheel setuptools build
	venv39/bin/pip install --upgrade pip wheel setuptools build
	venv310/bin/pip install --upgrade pip wheel setuptools build
	MONETDB_BRANCH=Jul2021 CFLAGS="-I/opt/homebrew/include -L/opt/homebrew/lib" venv38/bin/python -m build
	MONETDB_BRANCH=Jul2021 CFLAGS="-I/opt/homebrew/include -L/opt/homebrew/lib" venv39/bin/python -m build
	MONETDB_BRANCH=Jul2021 CFLAGS="-I/opt/homebrew/include -L/opt/homebrew/lib" venv310/bin/python -m build

osx-m1-wheel: venv/
	MONETDB_BRANCH=Jul2021 CFLAGS="-I/opt/homebrew/include -L/opt/homebrew/lib" venv/bin/python -m build
