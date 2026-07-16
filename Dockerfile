FROM python:3.14-slim

# The CLIs updee relies on for upgrading files:
# - uv (pyproject.toml, requirements.txt)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

# Let uv cache work when running as an arbitrary --user without a home:
ENV UV_CACHE_DIR=/tmp/uv-cache

# Install updee itself:
WORKDIR /updee
COPY pyproject.toml README.md ./
COPY src/ src/
# There is no git metadata inside the image, so give setuptools-scm a version:
ARG UPD_VERSION=0.0.0
ENV SETUPTOOLS_SCM_PRETEND_VERSION_FOR_UPD=$UPD_VERSION
RUN uv pip install --system --no-cache .

# Run updee in the repo / folder mounted at /repo:
WORKDIR /repo
ENTRYPOINT ["updee"]
