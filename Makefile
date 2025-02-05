
DOCKER_TAG ?= latest
export DOCKER_TAG
DOCKER_IMAGE = danduk82/yandex-stats
ROOT = $(dir $(realpath $(firstword $(MAKEFILE_LIST))))

all: push

.PHONY: pull build acceptance build_acceptance

build:
	docker build --tag=$(DOCKER_IMAGE):$(DOCKER_TAG) --build-arg BUILD_DATE="$$(date +%Y-%m-%d)" .

push: build
	docker push $(DOCKER_IMAGE):$(DOCKER_TAG)