from pathlib import Path

import updee.upgrade
from updee.upgrade import upgrade_file


class FakeCompletedProcess:
    def __init__(self, returncode):
        self.returncode = returncode


def test_pyproject_runs_uv_lock_upgrade(tmp_path, monkeypatch):
    calls = []

    def fake_run(command, cwd, stdout=None, stderr=None):
        calls.append((command, cwd))
        return FakeCompletedProcess(0)

    monkeypatch.setattr(updee.upgrade.subprocess, "run", fake_run)

    assert upgrade_file(tmp_path / "pyproject.toml") == "upgraded"
    assert calls == [(["uv", "lock", "--upgrade"], tmp_path)]


def test_pyproject_propagates_failure(tmp_path, monkeypatch):
    def fake_run(command, cwd, stdout=None, stderr=None):
        return FakeCompletedProcess(2)

    monkeypatch.setattr(updee.upgrade.subprocess, "run", fake_run)

    assert upgrade_file(tmp_path / "pyproject.toml") == "failed"


def test_requirements_txt_compiles_onto_itself(tmp_path, monkeypatch):
    calls = []

    def fake_run(command, cwd, stdout=None, stderr=None):
        calls.append((command, cwd))
        return FakeCompletedProcess(0)

    monkeypatch.setattr(updee.upgrade.subprocess, "run", fake_run)

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

    monkeypatch.setattr(updee.upgrade.subprocess, "run", fake_run)

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

    monkeypatch.setattr(updee.upgrade.subprocess, "run", fake_run)

    assert upgrade_file(tmp_path / "pyproject.toml") == "failed"
    assert "'uv' not found" in capsys.readouterr().out


def test_dry_run_does_not_run_anything(tmp_path, monkeypatch, capsys):
    def fake_run(command, cwd, stdout=None, stderr=None):
        raise AssertionError("subprocess.run should not be called in dry run")

    monkeypatch.setattr(updee.upgrade.subprocess, "run", fake_run)

    assert upgrade_file(tmp_path / "pyproject.toml", dry_run=True) == "would upgrade"
    output = capsys.readouterr().out
    assert "would run 'uv lock --upgrade'" in output


def test_quiet_hides_progress_and_subcommand_output(tmp_path, monkeypatch, capsys):
    calls = []

    def fake_run(command, cwd, stdout=None, stderr=None):
        calls.append((stdout, stderr))
        return FakeCompletedProcess(0)

    monkeypatch.setattr(updee.upgrade.subprocess, "run", fake_run)

    assert upgrade_file(tmp_path / "pyproject.toml", quiet=True) == "upgraded"
    assert capsys.readouterr().out == ""
    devnull = updee.upgrade.subprocess.DEVNULL
    assert calls == [(devnull, devnull)]


def test_unsupported_file_is_skipped(capsys):
    assert upgrade_file(Path("Makefile")) == "skipped"
    captured = capsys.readouterr()
    assert "skipping" in captured.out


def _successful_runs(monkeypatch):
    calls = []

    def fake_run(command, cwd, stdout=None, stderr=None):
        calls.append((command, cwd))
        return FakeCompletedProcess(0)

    monkeypatch.setattr(updee.upgrade.subprocess, "run", fake_run)
    return calls


def test_uv_lock_runs_uv_lock_upgrade(tmp_path, monkeypatch):
    calls = _successful_runs(monkeypatch)

    assert upgrade_file(tmp_path / "uv.lock") == "upgraded"
    assert calls == [(["uv", "lock", "--upgrade"], tmp_path)]


def test_pyproject_defers_to_uv_lock(tmp_path, monkeypatch, capsys):
    calls = _successful_runs(monkeypatch)
    (tmp_path / "pyproject.toml").write_text('[project]\nname = "x"\n')
    (tmp_path / "uv.lock").touch()

    assert upgrade_file(tmp_path / "pyproject.toml") == "skipped"
    assert calls == []
    assert "uv.lock is upgraded instead" in capsys.readouterr().out


def test_poetry_pyproject_is_skipped(tmp_path, monkeypatch, capsys):
    calls = _successful_runs(monkeypatch)
    (tmp_path / "pyproject.toml").write_text('[tool.poetry]\nname = "x"\n')

    assert upgrade_file(tmp_path / "pyproject.toml") == "skipped"
    assert calls == []
    assert "poetry" in capsys.readouterr().out


def test_poetry_lock_is_detected(tmp_path, monkeypatch, capsys):
    calls = _successful_runs(monkeypatch)
    (tmp_path / "pyproject.toml").write_text('[project]\nname = "x"\n')
    (tmp_path / "poetry.lock").touch()

    assert upgrade_file(tmp_path / "pyproject.toml") == "skipped"
    assert calls == []
    assert "poetry" in capsys.readouterr().out


def test_package_lock_runs_npm_update(tmp_path, monkeypatch):
    calls = _successful_runs(monkeypatch)

    assert upgrade_file(tmp_path / "package-lock.json") == "upgraded"
    assert calls == [(["npm", "update"], tmp_path)]


def test_package_json_bumps_ranges_and_installs(tmp_path, monkeypatch):
    calls = _successful_runs(monkeypatch)

    assert upgrade_file(tmp_path / "package.json") == "upgraded"
    assert calls == [
        (["npx", "--yes", "npm-check-updates", "-u"], tmp_path),
        (["npm", "install"], tmp_path),
    ]


def test_go_mod_runs_go_get_and_tidy(tmp_path, monkeypatch):
    calls = _successful_runs(monkeypatch)

    assert upgrade_file(tmp_path / "go.mod") == "upgraded"
    assert calls == [
        (["go", "get", "-u", "./..."], tmp_path),
        (["go", "mod", "tidy"], tmp_path),
    ]


def test_cargo_lock_runs_cargo_update(tmp_path, monkeypatch):
    calls = _successful_runs(monkeypatch)

    assert upgrade_file(tmp_path / "Cargo.lock") == "upgraded"
    assert calls == [(["cargo", "update"], tmp_path)]


def test_cargo_toml_without_lock_runs_cargo_update(tmp_path, monkeypatch):
    calls = _successful_runs(monkeypatch)

    assert upgrade_file(tmp_path / "Cargo.toml") == "upgraded"
    assert calls == [(["cargo", "update"], tmp_path)]


def test_cargo_toml_defers_to_cargo_lock(tmp_path, monkeypatch, capsys):
    calls = _successful_runs(monkeypatch)
    (tmp_path / "Cargo.lock").touch()

    assert upgrade_file(tmp_path / "Cargo.toml") == "skipped"
    assert calls == []
    assert "Cargo.lock is upgraded instead" in capsys.readouterr().out


def test_dry_run_prints_all_commands(tmp_path, monkeypatch, capsys):
    def fake_run(command, cwd, stdout=None, stderr=None):
        raise AssertionError("subprocess.run should not be called in dry run")

    monkeypatch.setattr(updee.upgrade.subprocess, "run", fake_run)

    assert upgrade_file(tmp_path / "go.mod", dry_run=True) == "would upgrade"
    output = capsys.readouterr().out
    assert "would run 'go get -u ./...', then 'go mod tidy'" in output


def test_failing_command_stops_the_plan(tmp_path, monkeypatch):
    calls = []

    def fake_run(command, cwd, stdout=None, stderr=None):
        calls.append(command)
        return FakeCompletedProcess(1)

    monkeypatch.setattr(updee.upgrade.subprocess, "run", fake_run)

    assert upgrade_file(tmp_path / "go.mod") == "failed"
    assert calls == [["go", "get", "-u", "./..."]]
