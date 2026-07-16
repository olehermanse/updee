# updee

Stupidly simple repo updater.

A CLI for keeping repos up to date, similar in spirit to updatecli, dependabot, and renovate.

**Note:** `updee` assumes you have the necessary programs installed (like npm, uv, etc.).
If not, it will give you a helpful error message.
Alternatively, use the docker image, which has all the tools installed.

**Note:** `updee` does not attempt to be a SaaS solution, chatbot, slack bot, GitHub PR bot.
It is simply a CLI which updates dependencies and commits those changes with nice commit messages.
The rest is left up to you, like when / where to run it and how to create pull requests.
It assumes you run it somewhere that makes those things easy for you (Such as in a GitHub Action).

## Docker

The Dockerfile builds an image with upd and the CLIs it relies on (uv).
Build it once, then run upd in any repo / folder by mounting it at `/repo`:

```bash
docker build -t updee .
docker run --rm --user "$(id -u):$(id -g)" -v "$PWD:/repo" updee
```

## Development

This project uses [uv](https://docs.astral.sh/uv/).

To run updee in this repo without installing it:

```bash
uv run updee
```

## Development

Run formatting, linting, and tests:

```bash
make check
```
