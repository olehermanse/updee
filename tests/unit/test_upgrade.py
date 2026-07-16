from pathlib import Path

import upd.upgrade
from upd.upgrade import upgrade_file


class FakeCompletedProcess:
    def __init__(self, returncode):
        self.returncode = returncode


def test_pyproject_runs_uv_lock_upgrade(tmp_path, monkeypatch):
    calls = []

    def fake_run(command, cwd):
        calls.append((command, cwd))
        return FakeCompletedProcess(0)

    monkeypatch.setattr(upd.upgrade.subprocess, "run", fake_run)

    assert upgrade_file(tmp_path / "pyproject.toml") == 0
    assert calls == [(["uv", "lock", "--upgrade"], tmp_path)]


def test_pyproject_propagates_failure(tmp_path, monkeypatch):
    def fake_run(command, cwd):
        return FakeCompletedProcess(2)

    monkeypatch.setattr(upd.upgrade.subprocess, "run", fake_run)

    assert upgrade_file(tmp_path / "pyproject.toml") == 2


def test_requirements_txt_compiles_onto_itself(tmp_path, monkeypatch):
    calls = []

    def fake_run(command, cwd):
        calls.append((command, cwd))
        return FakeCompletedProcess(0)

    monkeypatch.setattr(upd.upgrade.subprocess, "run", fake_run)

    assert upgrade_file(tmp_path / "requirements.txt") == 0
    assert calls == [
        (
            [
                "uv",
                "pip",
                "compile",
                "requirements.txt",
                "-o",
                "requirements.txt",
                "--upgrade",
            ],
            tmp_path,
        )
    ]


def test_requirements_txt_compiles_from_requirements_in(tmp_path, monkeypatch):
    (tmp_path / "requirements.in").touch()
    calls = []

    def fake_run(command, cwd):
        calls.append((command, cwd))
        return FakeCompletedProcess(0)

    monkeypatch.setattr(upd.upgrade.subprocess, "run", fake_run)

    assert upgrade_file(tmp_path / "requirements.txt") == 0
    assert calls == [
        (
            [
                "uv",
                "pip",
                "compile",
                "requirements.in",
                "-o",
                "requirements.txt",
                "--upgrade",
            ],
            tmp_path,
        )
    ]


def test_missing_uv_is_an_error(tmp_path, monkeypatch, capsys):
    def fake_run(command, cwd):
        raise FileNotFoundError()

    monkeypatch.setattr(upd.upgrade.subprocess, "run", fake_run)

    assert upgrade_file(tmp_path / "pyproject.toml") == 1
    assert "'uv' not found" in capsys.readouterr().out


def test_unsupported_file_is_skipped(capsys):
    assert upgrade_file(Path("package.json")) == 0
    captured = capsys.readouterr()
    assert "skipping" in captured.out
