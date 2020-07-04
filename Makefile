
GITHUB_WORKSPACE=/build
DOCKER_IMAGE=gijzelaerr/monetdb


all: test

venv/:
	python3 -m venv venv
	venv/bin/pip install --upgrade pip wheel

venv/installed: venv/
	venv/bin/pip install -e ".[test]"
	touch venv/installed

setup: venv/installed

test: setup
	venv/bin/pytest 


docker-build:
	docker build -t $(DOCKER_IMAGE):wheel -f docker/wheel.docker .
	docker build -t $(DOCKER_IMAGE):test38 -f docker/test38.docker .

docker-force-build:
	docker build --no-cache -t $(DOCKER_IMAGE):wheel -f docker/wheel.docker .
	docker build --no-cache -t $(DOCKER_IMAGE):test38 -f docker/test38.docker .


docker-wheels: docker-build venv/
	venv/bin/python setup.py sdist
	docker run -v `pwd`:$(GITHUB_WORKSPACE) $(DOCKER_IMAGE):wheel sh -c "cd $(GITHUB_WORKSPACE); .inside/make_wheel.sh 3.6"
	docker run -v `pwd`:$(GITHUB_WORKSPACE) $(DOCKER_IMAGE):wheel sh -c "cd $(GITHUB_WORKSPACE); .inside/make_wheel.sh 3.7"
	docker run -v `pwd`:$(GITHUB_WORKSPACE) $(DOCKER_IMAGE):wheel sh -c "cd $(GITHUB_WORKSPACE); .inside/make_wheel.sh 3.8"
	
docker-shell:
	docker run -ti -v `pwd`:$(GITHUB_WORKSPACE) $(DOCKER_IMAGE):test38 sh -c "cd $(GITHUB_WORKSPACE); bash"

docker-test: docker-build
	docker run -ti -v `pwd`:$(GITHUB_WORKSPACE) $(DOCKER_IMAGE):test38 sh -c "cd $(GITHUB_WORKSPACE); .inside/test.sh"

docker-mypy: docker-build
	docker run -v `pwd`:$(GITHUB_WORKSPACE) $(DOCKER_IMAGE):test38 sh -c "cd $(GITHUB_WORKSPACE); .inside/mypy.sh"

docker-pycodestyle: docker-build
	docker run -v `pwd`:$(GITHUB_WORKSPACE) $(DOCKER_IMAGE):test38 sh -c "cd $(GITHUB_WORKSPACE); .inside/pycodestyle.sh"

docker-info: docker-build
	docker run -v `pwd`:$(GITHUB_WORKSPACE) $(DOCKER_IMAGE):test38 sh -c "cd $(GITHUB_WORKSPACE); .inside/info.sh"

docker-doc:
	docker build -t $(DOCKER_IMAGE):doc -f docker/doc.docker .

docker-push: docker-build
	docker push $(DOCKER_IMAGE):wheel
	docker push $(DOCKER_IMAGE):test38

clean: venv/
	venv/bin/python3 setup.py clean
	rm -rf build dist *.egg-info .eggs monetdbe/*.so monetdbe/*.dylib .*_cache venv/

venv/bin/mypy: venv/
	venv/bin/pip install mypy

venv/bin/pycodestyle: venv/
	venv/bin/pip install pycodestyle

mypy: venv/bin/mypy
	venv/bin/mypy monetdbe tests

pycodestyle: venv/bin/pycodestyle
	venv/bin/pycodestyle monetdbe tests

venv/bin/jupyter-notebook: venv/
	venv/bin/pip install notebook

notebook: venv/bin/jupyter-notebook
	venv/bin/jupyter-notebook
