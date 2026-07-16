from pathlib import Path

import upd.upgrade
from upd.upgrade import upgrade_file


class FakeCompletedProcess:
    def __init__(self, returncode):
        self.returncode = returncode


def test_pyproject_runs_uv_lock_upgrade(tmp_path, monkeypatch):
    calls = []

    def fake_run(command, cwd, stdout=None, stderr=None):
        calls.append((command, cwd))
        return FakeCompletedProcess(0)

    monkeypatch.setattr(upd.upgrade.subprocess, "run", fake_run)

    assert upgrade_file(tmp_path / "pyproject.toml") == "upgraded"
    assert calls == [(["uv", "lock", "--upgrade"], tmp_path)]


def test_pyproject_propagates_failure(tmp_path, monkeypatch):
    def fake_run(command, cwd, stdout=None, stderr=None):
        return FakeCompletedProcess(2)

    monkeypatch.setattr(upd.upgrade.subprocess, "run", fake_run)

    assert upgrade_file(tmp_path / "pyproject.toml") == "failed"


def test_requirements_txt_compiles_onto_itself(tmp_path, monkeypatch):
    calls = []

    def fake_run(command, cwd, stdout=None, stderr=None):
        calls.append((command, cwd))
        return FakeCompletedProcess(0)

    monkeypatch.setattr(upd.upgrade.subprocess, "run", fake_run)

    assert upgrade_file(tmp_path / "requirements.txt") == "upgraded"
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

    def fake_run(command, cwd, stdout=None, stderr=None):
        calls.append((command, cwd))
        return FakeCompletedProcess(0)

    monkeypatch.setattr(upd.upgrade.subprocess, "run", fake_run)

    assert upgrade_file(tmp_path / "requirements.txt") == "upgraded"
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
    def fake_run(command, cwd, stdout=None, stderr=None):
        raise FileNotFoundError()

    monkeypatch.setattr(upd.upgrade.subprocess, "run", fake_run)

    assert upgrade_file(tmp_path / "pyproject.toml") == "failed"
    assert "'uv' not found" in capsys.readouterr().out


def test_dry_run_does_not_run_anything(tmp_path, monkeypatch, capsys):
    def fake_run(command, cwd, stdout=None, stderr=None):
        raise AssertionError("subprocess.run should not be called in dry run")

    monkeypatch.setattr(upd.upgrade.subprocess, "run", fake_run)

    assert upgrade_file(tmp_path / "pyproject.toml", dry_run=True) == "would upgrade"
    output = capsys.readouterr().out
    assert "would run 'uv lock --upgrade'" in output


def test_quiet_hides_progress_and_subcommand_output(tmp_path, monkeypatch, capsys):
    calls = []

    def fake_run(command, cwd, stdout=None, stderr=None):
        calls.append((stdout, stderr))
        return FakeCompletedProcess(0)

    monkeypatch.setattr(upd.upgrade.subprocess, "run", fake_run)

    assert upgrade_file(tmp_path / "pyproject.toml", quiet=True) == "upgraded"
    assert capsys.readouterr().out == ""
    devnull = upd.upgrade.subprocess.DEVNULL
    assert calls == [(devnull, devnull)]


def test_unsupported_file_is_skipped(capsys):
    assert upgrade_file(Path("package.json")) == "skipped"
    captured = capsys.readouterr()
    assert "skipping" in captured.out
