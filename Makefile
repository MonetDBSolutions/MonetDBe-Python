
.PHONY: wheels tests docker

GITHUB_WORKSPACE=/build
DOCKER_IMAGE=gijzelaerr/monetdb


all: docker

docker:

force-build:
	docker build --no-cache -t $(DOCKER_IMAGE) .


wheels: docker
	docker run -v `pwd`:$(GITHUB_WORKSPACE) $(DOCKER_IMAGE) sh -c "cd $(GITHUB_WORKSPACE); .inside/make_wheel.sh 3.6"
	docker run -v `pwd`:$(GITHUB_WORKSPACE) $(DOCKER_IMAGE) sh -c "cd $(GITHUB_WORKSPACE); .inside/make_wheel.sh 3.7"
	docker run -v `pwd`:$(GITHUB_WORKSPACE) $(DOCKER_IMAGE) sh -c "cd $(GITHUB_WORKSPACE); .inside/make_wheel.sh 3.8"

tests:
	docker run -v `pwd`:$(GITHUB_WORKSPACE) $(DOCKER_IMAGE) sh -c "cd $(GITHUB_WORKSPACE); .inside/test.sh 3.6"
	docker run -v `pwd`:$(GITHUB_WORKSPACE) $(DOCKER_IMAGE) sh -c "cd $(GITHUB_WORKSPACE); .inside/test.sh 3.7"
	docker run -v `pwd`:$(GITHUB_WORKSPACE) $(DOCKER_IMAGE) sh -c "cd $(GITHUB_WORKSPACE); .inside/test.sh 3.8"

push: docker
	docker push $(DOCKER_IMAGE)
