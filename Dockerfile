FROM python:3.14-slim

# The CLIs updee relies on for upgrading files:
# - uv (pyproject.toml, requirements.txt, uv.lock)
# - npm / npx with npm-check-updates (package.json, package-lock.json)
# - go (go.mod)
# - cargo (Cargo.toml, Cargo.lock)
# - git, used by the above to fetch dependencies
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/
RUN apt-get update \
    && apt-get install -y --no-install-recommends git nodejs npm golang cargo \
    && rm -rf /var/lib/apt/lists/* \
    && npm install --global npm-check-updates

# Let the tools' caches work when running as an arbitrary --user without a home:
ENV UV_CACHE_DIR=/tmp/uv-cache
ENV npm_config_cache=/tmp/npm-cache
ENV GOPATH=/tmp/go
ENV GOCACHE=/tmp/go-build
ENV CARGO_HOME=/tmp/cargo

# Install updee itself:
WORKDIR /updee
COPY pyproject.toml README.md ./
COPY src/ src/
# There is no git metadata inside the image, so give setuptools-scm a version:
ARG UPDEE_VERSION=0.0.0
ENV SETUPTOOLS_SCM_PRETEND_VERSION_FOR_UPDEE=$UPDEE_VERSION
RUN uv pip install --system --no-cache .

# Run updee in the repo / folder mounted at /repo:
WORKDIR /repo
ENTRYPOINT ["updee"]
