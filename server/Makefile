REGISTRY?=ghcr.io
IMAGE_NAME?=k-phoen/weather-display
IMAGE_VERSION?=latest

.PHONY: run
run:
	uv run waitress-serve --host 127.0.0.1 app.app

.PHONY: build
build:
	docker build -t ${REGISTRY}/${IMAGE_NAME}:${IMAGE_VERSION} .

.PHONY: push
push:
	docker push ${REGISTRY}/${IMAGE_NAME}:${IMAGE_VERSION}