import urllib.error

import updee.workflows
from updee.upgrade import upgrade_file
from updee.workflows import latest_version, update_actions

WORKFLOW = """\
name: CI
on: push
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5.0.0
        with:
          python-version: "3.12"
"""


def fake_latest(versions):
    def lookup(repo):
        return versions[repo]

    return lookup


def test_updates_refs_keeping_their_precision(monkeypatch):
    monkeypatch.setattr(
        updee.workflows,
        "latest_version",
        fake_latest({"actions/checkout": "v5.0.2", "actions/setup-python": "v6.1.0"}),
    )

    content, changes = update_actions(WORKFLOW)
    assert "uses: actions/checkout@v5\n" in content
    assert "uses: actions/setup-python@v6.1.0\n" in content
    assert 'python-version: "3.12"' in content
    assert changes == [
        "actions/checkout v4 -> v5",
        "actions/setup-python v5.0.0 -> v6.1.0",
    ]


def test_looks_up_the_repo_for_subpath_actions(monkeypatch):
    lookups = []

    def lookup(repo):
        lookups.append(repo)
        return "v4.0.0"

    monkeypatch.setattr(updee.workflows, "latest_version", lookup)

    content, _ = update_actions("      - uses: github/codeql-action/init@v3\n")
    assert lookups == ["github/codeql-action"]
    assert content == "      - uses: github/codeql-action/init@v4\n"


def test_queries_each_repo_only_once(monkeypatch):
    lookups = []

    def lookup(repo):
        lookups.append(repo)
        return "v5"

    monkeypatch.setattr(updee.workflows, "latest_version", lookup)

    content, _ = update_actions(
        "      - uses: actions/checkout@v3\n      - uses: actions/checkout@v4\n"
    )
    assert lookups == ["actions/checkout"]
    assert content == (
        "      - uses: actions/checkout@v5\n      - uses: actions/checkout@v5\n"
    )


def test_leaves_non_version_refs_alone(monkeypatch):
    def lookup(repo):
        raise AssertionError("should not query the API")

    monkeypatch.setattr(updee.workflows, "latest_version", lookup)

    content = (
        "      - uses: actions/checkout@8f4b7f84864484a7bf31766abe9204da3cbe65b3\n"
        "      - uses: actions/checkout@main\n"
        "      - uses: ./.github/actions/local\n"
        "      - uses: docker://alpine:3.20\n"
        "      - run: echo not a uses line\n"
    )
    assert update_actions(content) == (content, [])


def test_preserves_trailing_comments(monkeypatch):
    monkeypatch.setattr(updee.workflows, "latest_version", lambda repo: "v2.1.3")

    content, _ = update_actions("      - uses: foo/bar@v1 # pinned\n")
    assert content == "      - uses: foo/bar@v2 # pinned\n"


def test_latest_tag_with_fewer_components(monkeypatch):
    monkeypatch.setattr(updee.workflows, "latest_version", lambda repo: "v2")

    content, _ = update_actions("      - uses: foo/bar@v1.2.3\n")
    assert content == "      - uses: foo/bar@v2\n"


def test_skips_actions_without_usable_releases(monkeypatch):
    monkeypatch.setattr(
        updee.workflows,
        "latest_version",
        fake_latest({"foo/norelease": None, "foo/weird": "v2-beta"}),
    )

    content = "      - uses: foo/norelease@v1\n      - uses: foo/weird@v1\n"
    assert update_actions(content) == (content, [])


def _workflow_path(tmp_path):
    directory = tmp_path / ".github" / "workflows"
    directory.mkdir(parents=True)
    return directory / "ci.yml"


def test_upgrade_file_rewrites_workflow(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(updee.workflows, "latest_version", lambda repo: "v5.0.2")
    path = _workflow_path(tmp_path)
    path.write_text("      - uses: actions/checkout@v4\n")

    assert upgrade_file(path) == "upgraded"
    assert path.read_text() == "      - uses: actions/checkout@v5\n"
    assert "actions/checkout v4 -> v5" in capsys.readouterr().out


def test_workflow_already_up_to_date(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(updee.workflows, "latest_version", lambda repo: "v4.2.2")
    path = _workflow_path(tmp_path)
    path.write_text("      - uses: actions/checkout@v4\n")

    assert upgrade_file(path) == "upgraded"
    assert path.read_text() == "      - uses: actions/checkout@v4\n"
    assert "up to date" in capsys.readouterr().out


def test_workflow_dry_run_does_not_query_or_write(tmp_path, monkeypatch, capsys):
    def lookup(repo):
        raise AssertionError("should not query the API in dry run")

    monkeypatch.setattr(updee.workflows, "latest_version", lookup)
    path = _workflow_path(tmp_path)
    path.write_text("      - uses: actions/checkout@v4\n")

    assert upgrade_file(path, dry_run=True) == "would upgrade"
    assert path.read_text() == "      - uses: actions/checkout@v4\n"
    assert "would update" in capsys.readouterr().out


def test_workflow_api_failure(tmp_path, monkeypatch, capsys):
    def lookup(repo):
        raise urllib.error.URLError("no network")

    monkeypatch.setattr(updee.workflows, "latest_version", lookup)
    path = _workflow_path(tmp_path)
    path.write_text("      - uses: actions/checkout@v4\n")

    assert upgrade_file(path) == "failed"
    assert "GitHub API request failed" in capsys.readouterr().out


def test_workflow_quiet_hides_progress(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(updee.workflows, "latest_version", lambda repo: "v5")
    path = _workflow_path(tmp_path)
    path.write_text("      - uses: actions/checkout@v4\n")

    assert upgrade_file(path, quiet=True) == "upgraded"
    assert capsys.readouterr().out == ""


class FakeResponse:
    def __init__(self, body):
        self.body = body

    def read(self):
        return self.body

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


def test_latest_version_returns_tag_name(monkeypatch):
    requests = []

    def fake_urlopen(request, timeout=None):
        requests.append(request)
        return FakeResponse(b'{"tag_name": "v5.0.2"}')

    monkeypatch.setattr(updee.workflows.urllib.request, "urlopen", fake_urlopen)
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)

    assert latest_version("actions/checkout") == "v5.0.2"
    url = "https://api.github.com/repos/actions/checkout/releases/latest"
    assert requests[0].full_url == url
    assert requests[0].get_header("Authorization") is None


def test_latest_version_none_when_no_releases(monkeypatch):
    def fake_urlopen(request, timeout=None):
        raise urllib.error.HTTPError(request.full_url, 404, "Not Found", None, None)

    monkeypatch.setattr(updee.workflows.urllib.request, "urlopen", fake_urlopen)

    assert latest_version("foo/bar") is None


def test_latest_version_sends_github_token(monkeypatch):
    requests = []

    def fake_urlopen(request, timeout=None):
        requests.append(request)
        return FakeResponse(b'{"tag_name": "v1"}')

    monkeypatch.setattr(updee.workflows.urllib.request, "urlopen", fake_urlopen)
    monkeypatch.setenv("GITHUB_TOKEN", "secret123")

    assert latest_version("foo/bar") == "v1"
    assert requests[0].get_header("Authorization") == "Bearer secret123"
