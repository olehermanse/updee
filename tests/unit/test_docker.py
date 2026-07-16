import urllib.error

import updee.docker
from updee.docker import image_tags, latest_tag, update_base_images
from updee.upgrade import upgrade_file

PYTHON_TAGS = ["3.14-slim", "3.14.0-slim", "3.14", "3.14.0", "latest", "3-slim"]


def test_updates_from_lines_keeping_shape(monkeypatch):
    monkeypatch.setattr(updee.docker, "image_tags", lambda image: PYTHON_TAGS)

    content, changes = update_base_images("FROM python:3.11-slim\n")
    assert content == "FROM python:3.14-slim\n"
    assert changes == ["python 3.11-slim -> 3.14-slim"]


def test_preserves_stage_names_and_platform(monkeypatch):
    monkeypatch.setattr(updee.docker, "image_tags", lambda image: PYTHON_TAGS)

    content, _ = update_base_images(
        "FROM --platform=linux/amd64 python:3.11-slim AS builder\n"
    )
    assert content == "FROM --platform=linux/amd64 python:3.14-slim AS builder\n"


def test_queries_each_image_only_once(monkeypatch):
    lookups = []

    def lookup(image):
        lookups.append(image)
        return PYTHON_TAGS

    monkeypatch.setattr(updee.docker, "image_tags", lookup)

    content, _ = update_base_images(
        "FROM python:3.10-slim AS builder\nFROM python:3.11-slim\n"
    )
    assert lookups == ["python"]
    assert content == "FROM python:3.14-slim AS builder\nFROM python:3.14-slim\n"


def test_leaves_non_version_tags_and_other_lines_alone(monkeypatch):
    def lookup(image):
        raise AssertionError("should not query Docker Hub")

    monkeypatch.setattr(updee.docker, "image_tags", lookup)

    content = (
        "# FROM python:3.11-slim\n"
        "FROM scratch\n"
        "FROM python:latest\n"
        "FROM python:3.11-slim@sha256:abc123\n"
        "COPY --from=builder /app /app\n"
    )
    assert update_base_images(content) == (content, [])


def test_leaves_images_outside_docker_hub_alone(monkeypatch):
    monkeypatch.setattr(updee.docker, "image_tags", lambda image: None)

    content = "FROM ghcr.io/astral-sh/uv:0.1.0\n"
    assert update_base_images(content) == (content, [])


def test_latest_tag_matches_precision_and_suffix():
    tags = ["3.14-slim", "3.14.2-slim", "3.14", "3.14-alpine", "3-slim", "bookworm"]
    assert latest_tag("3.11-slim", tags) == "3.14-slim"
    assert latest_tag("3.11.2-slim", tags) == "3.14.2-slim"
    assert latest_tag("3.11", tags) == "3.14"
    assert latest_tag("3.11-alpine", tags) == "3.14-alpine"
    assert latest_tag("3", tags) is None


def test_latest_tag_never_downgrades():
    assert latest_tag("3.15", ["3.14", "3.13"]) is None
    assert latest_tag("3.14", ["3.14"]) is None


def test_latest_tag_respects_v_prefix():
    assert latest_tag("v1.2", ["v1.3", "2.0"]) == "v1.3"
    assert latest_tag("1.2", ["v9.9", "1.3"]) == "1.3"


def test_latest_tag_ignores_non_versions():
    assert latest_tag("latest", ["3.14"]) is None
    assert latest_tag("3.11", ["bookworm", "3.12rc1"]) is None


class FakeResponse:
    def __init__(self, body):
        self.body = body

    def read(self):
        return self.body

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


def test_image_tags_official_image_with_pagination(monkeypatch):
    pages = {
        "https://hub.docker.com/v2/repositories/library/python/tags?page_size=100": (
            b'{"results": [{"name": "3.14-slim"}], "next": "https://next.page"}'
        ),
        "https://next.page": b'{"results": [{"name": "3.13-slim"}], "next": null}',
    }
    requests = []

    def fake_urlopen(request, timeout=None):
        requests.append(request.full_url)
        return FakeResponse(pages[request.full_url])

    monkeypatch.setattr(updee.docker.urllib.request, "urlopen", fake_urlopen)

    assert image_tags("python") == ["3.14-slim", "3.13-slim"]
    assert len(requests) == 2


def test_image_tags_user_repository(monkeypatch):
    requests = []

    def fake_urlopen(request, timeout=None):
        requests.append(request.full_url)
        return FakeResponse(b'{"results": [{"name": "1.0"}], "next": null}')

    monkeypatch.setattr(updee.docker.urllib.request, "urlopen", fake_urlopen)

    assert image_tags("grafana/grafana") == ["1.0"]
    assert requests == [
        "https://hub.docker.com/v2/repositories/grafana/grafana/tags?page_size=100"
    ]


def test_image_tags_not_on_docker_hub(monkeypatch):
    def fake_urlopen(request, timeout=None):
        raise AssertionError("should not query Docker Hub")

    monkeypatch.setattr(updee.docker.urllib.request, "urlopen", fake_urlopen)

    assert image_tags("ghcr.io/astral-sh/uv") is None
    assert image_tags("registry.example.com:5000/image") is None
    assert image_tags("deep/nested/image") is None


def test_image_tags_unknown_image(monkeypatch):
    def fake_urlopen(request, timeout=None):
        raise urllib.error.HTTPError(request.full_url, 404, "Not Found", None, None)

    monkeypatch.setattr(updee.docker.urllib.request, "urlopen", fake_urlopen)

    assert image_tags("nosuchimage") is None


def test_upgrade_file_rewrites_dockerfile(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(updee.docker, "image_tags", lambda image: PYTHON_TAGS)
    path = tmp_path / "Dockerfile"
    path.write_text("FROM python:3.11-slim\nRUN echo hello\n")

    assert upgrade_file(path) == "upgraded"
    assert path.read_text() == "FROM python:3.14-slim\nRUN echo hello\n"
    assert "python 3.11-slim -> 3.14-slim" in capsys.readouterr().out


def test_dockerfile_already_up_to_date(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(updee.docker, "image_tags", lambda image: PYTHON_TAGS)
    path = tmp_path / "Dockerfile"
    path.write_text("FROM python:3.14-slim\n")

    assert upgrade_file(path) == "upgraded"
    assert path.read_text() == "FROM python:3.14-slim\n"
    assert "up to date" in capsys.readouterr().out


def test_dockerfile_dry_run_does_not_query_or_write(tmp_path, monkeypatch, capsys):
    def lookup(image):
        raise AssertionError("should not query Docker Hub in dry run")

    monkeypatch.setattr(updee.docker, "image_tags", lookup)
    path = tmp_path / "Dockerfile"
    path.write_text("FROM python:3.11-slim\n")

    assert upgrade_file(path, dry_run=True) == "would upgrade"
    assert path.read_text() == "FROM python:3.11-slim\n"
    assert "would update" in capsys.readouterr().out


def test_dockerfile_api_failure(tmp_path, monkeypatch, capsys):
    def lookup(image):
        raise urllib.error.URLError("no network")

    monkeypatch.setattr(updee.docker, "image_tags", lookup)
    path = tmp_path / "Dockerfile"
    path.write_text("FROM python:3.11-slim\n")

    assert upgrade_file(path) == "failed"
    assert "Docker Hub API request failed" in capsys.readouterr().out


def test_dockerfile_quiet_hides_progress(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(updee.docker, "image_tags", lambda image: PYTHON_TAGS)
    path = tmp_path / "Dockerfile"
    path.write_text("FROM python:3.11-slim\n")

    assert upgrade_file(path, quiet=True) == "upgraded"
    assert capsys.readouterr().out == ""
