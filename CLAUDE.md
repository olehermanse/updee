# upd information for LLMs

`updee` is a stupidly simple repo updater - a CLI for keeping repos up to date, similar in spirit to updatecli, dependabot, and renovate.

## Running python tools

This project uses `uv`.
That means that you should not run `python`, `python3`, `pip`, `pip3` directly.
Instead, run the appropriate uv command to ensure we're using the right python and the right dependencies.

To run the CLI:

```bash
uv run updee
```

## Running tests

In general, the main command to run for testing is:

```bash
make check
```

This will run formatting, linting, and all the test suites.
To run only the unit tests:

```bash
uv run pytest
```

## Test suites

- Unit tests in `tests/unit` test individual python functions.
- Shell tests in `tests/shell` test the tool as a whole in an end-to-end fashion - each script sets up a fake "repo" under `out/shell-tests/` and checks that `updee` upgrades it. They require network access. Since new upstream releases happen at any time, they check that files were changed and remain valid, never exact post-upgrade versions.

## Fix the implementation

In general, when the prompter asks you to fix the implementation, this means that they have adjusted the tests already and they want you to fix the implementation.
Typically you should not touch the tests in this case, unless there is something obviously wrong in them, like a typo.
The first step to identify what is necessary should be to run the tests and see which ones are failing.

## Changelog

`CHANGELOG.md` follows the [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) format.
When making user-visible changes, add an entry under the `[Unreleased]` heading, in the appropriate subsection (`Added`, `Changed`, `Deprecated`, `Removed`, `Fixed`, `Security`).

## Pointers for the source code

- The CLI entry point (`main()`) is in `src/updee/main.py`.
- Discovery of upgradeable files (package.json, pyproject.toml, etc.) is in `src/updee/find.py`.
- Upgrading of the discovered files (running commands like `uv lock --upgrade`) is in `src/updee/upgrade.py`.
- Upgrading of GitHub Actions workflows (querying the GitHub API for the latest release tags) is in `src/updee/workflows.py`.
- Unit tests are in `tests/unit`.
- Shell tests are in `tests/shell`.
- The version is derived from git tags via setuptools-scm - there is no version constant in the source code. `src/updee/version.py` reads it from the installed package metadata.
- The `Dockerfile` builds an image for running updee in a repo / folder mounted at `/repo`. It must install every CLI that `src/updee/upgrade.py` shells out to (currently only uv) - update it when adding upgraders that need new tools.

## Reference project

Use CFEngine CLI as a reference for how to do something.
It is cloned in tmp/cfengine-cli.

## Committing

In general you should commit your work unless told otherwise.
AI-generated commits should be clearly labelled at the end of the commit message:

```
Co-authored-by: Claude Fable 5 <noreply@anthropic.com>
```
