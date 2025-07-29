FROM ghcr.io/astral-sh/uv:python3.13-alpine

ADD . /app

WORKDIR /app
RUN uv --no-cache sync --locked

CMD ["uv", "--no-cache", "run", "waitress-serve", "--host", "0.0.0.0", "app.app"]