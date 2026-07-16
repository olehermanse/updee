# upd

Stupidly simple repo updater.

A CLI for keeping repos up to date, similar in spirit to updatecli, dependabot, and renovate.

**Note:** upd assumes you have the necessary programs installed (like npm, uv, etc.).
If not, it will give you a helpful error message.
Alternatively, use the docker image, which has all the tools installed.

## Docker

The Dockerfile builds an image with upd and the CLIs it relies on (uv).
Build it once, then run upd in any repo / folder by mounting it at `/repo`:

```bash
docker build -t upd .
docker run --rm --user "$(id -u):$(id -g)" -v "$PWD:/repo" upd
```

## Development

This project uses [uv](https://docs.astral.sh/uv/).

To run upd in this repo without installing it:

```bash
uv run upd
```

## Development

Run formatting, linting, and tests:

```bash
make check
```
