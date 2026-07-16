# upd

Stupidly simple repo updater.

A CLI for keeping repos up to date, similar in spirit to updatecli, dependabot, and renovate.

**Note:** upd assumes you have the necessary programs installed (like npm, uv, etc.).
If not, it will give you a helpful error message.
We plan to add a dockerfile you can run which has all the tools installed as well.

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
