
.PHONY: wheels tests docker

GITHUB_WORKSPACE=/build
DOCKER_IMAGE=gijzelaerr/monetdb


all: docker

docker:
	docker build -t $(DOCKER_IMAGE):wheel -f docker/wheel.docker .
	docker build -t $(DOCKER_IMAGE):wheel -f docker/test38.docker .

force-build:
	docker build --force-build -t $(DOCKER_IMAGE):wheel -f docker/wheel.docker .
	docker build --force-build -t $(DOCKER_IMAGE):wheel -f docker/test38.docker .


wheels: docker
	docker run -v `pwd`:$(GITHUB_WORKSPACE) $(DOCKER_IMAGE) sh -c "cd $(GITHUB_WORKSPACE); .inside/make_wheel.sh 3.6"
	docker run -v `pwd`:$(GITHUB_WORKSPACE) $(DOCKER_IMAGE) sh -c "cd $(GITHUB_WORKSPACE); .inside/make_wheel.sh 3.7"
	docker run -v `pwd`:$(GITHUB_WORKSPACE) $(DOCKER_IMAGE) sh -c "cd $(GITHUB_WORKSPACE); .inside/make_wheel.sh 3.8"
	
shell:
	docker run -ti -v `pwd`:$(GITHUB_WORKSPACE) $(DOCKER_IMAGE) sh -c "cd $(GITHUB_WORKSPACE); bash"

tests:
	docker run -v `pwd`:$(GITHUB_WORKSPACE) $(DOCKER_IMAGE) sh -c "cd $(GITHUB_WORKSPACE); .inside/test.sh 3.6"
	docker run -v `pwd`:$(GITHUB_WORKSPACE) $(DOCKER_IMAGE) sh -c "cd $(GITHUB_WORKSPACE); .inside/test.sh 3.7"
	docker run -v `pwd`:$(GITHUB_WORKSPACE) $(DOCKER_IMAGE) sh -c "cd $(GITHUB_WORKSPACE); .inside/test.sh 3.8"

push: docker
	docker push $(DOCKER_IMAGE):wheel
