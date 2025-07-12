REGISTRY?=ghcr.io
IMAGE_NAME?=weather-display-server
IMAGE_VERSION?=latest

run:
	uv run waitress-serve --host 127.0.0.1 app.app

build:
	docker build -t ${REGISTRY}/${IMAGE_NAME}:${IMAGE_VERSION} .