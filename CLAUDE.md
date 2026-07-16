# upd information for LLMs

`upd` is a stupidly simple repo updater - a CLI for keeping repos up to date, similar in spirit to updatecli, dependabot, and renovate.

## Running python tools

This project uses `uv`.
That means that you should not run `python`, `python3`, `pip`, `pip3` directly.
Instead, run the appropriate uv command to ensure we're using the right python and the right dependencies.

To run the CLI:

```bash
uv run upd
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

## Fix the implementation

In general, when the prompter asks you to fix the implementation, this means that they have adjusted the tests already and they want you to fix the implementation.
Typically you should not touch the tests in this case, unless there is something obviously wrong in them, like a typo.
The first step to identify what is necessary should be to run the tests and see which ones are failing.

## Pointers for the source code

- The CLI entry point (`main()`) is in `src/upd/main.py`.
- Discovery of upgradeable files (package.json, pyproject.toml, etc.) is in `src/upd/find.py`.
- Unit tests are in `tests/unit`.
- The version is derived from git tags via setuptools-scm - there is no version constant in the source code.

## Reference project

Use CFEngine CLI as a reference for how to do something.
It is cloned in tmp/cfengine-cli.
