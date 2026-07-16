from importlib.metadata import PackageNotFoundError

import upd.version
from upd.version import version_string


def test_version_string_is_not_empty():
    assert version_string() != ""
    assert version_string() != "unknown"


def test_version_string_when_package_not_installed(monkeypatch):
    def fake_version(name):
        raise PackageNotFoundError(name)

    monkeypatch.setattr(upd.version, "version", fake_version)
    assert version_string() == "unknown"
