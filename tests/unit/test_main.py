import pytest

import upd.upgrade
from upd.main import main


def test_main_upgrades_found_files(tmp_path, capsys, monkeypatch):
    (tmp_path / "pyproject.toml").touch()
    monkeypatch.chdir(tmp_path)

    calls = []

    def fake_run(command, cwd):
        calls.append((command, cwd))

        class Result:
            returncode = 0

        return Result()

    monkeypatch.setattr(upd.upgrade.subprocess, "run", fake_run)

    assert main([]) == 0
    assert len(calls) == 1
    assert calls[0][0] == ["uv", "lock", "--upgrade"]


def test_main_propagates_upgrade_failure(tmp_path, capsys, monkeypatch):
    (tmp_path / "pyproject.toml").touch()
    monkeypatch.chdir(tmp_path)

    def fake_run(command, cwd):
        class Result:
            returncode = 2

        return Result()

    monkeypatch.setattr(upd.upgrade.subprocess, "run", fake_run)

    assert main([]) == 1


def test_main_skips_unsupported_files(tmp_path, capsys, monkeypatch):
    (tmp_path / "package.json").touch()
    monkeypatch.chdir(tmp_path)

    assert main([]) == 0
    assert "skipping" in capsys.readouterr().out


def test_main_with_no_upgrade_files(tmp_path, capsys, monkeypatch):
    monkeypatch.chdir(tmp_path)

    assert main([]) == 1
    captured = capsys.readouterr()
    assert captured.out == "No files to upgrade found\n"


def test_main_path_to_directory(tmp_path, capsys, monkeypatch):
    (tmp_path / "one").mkdir()
    (tmp_path / "one" / "package.json").touch()
    (tmp_path / "two").mkdir()
    (tmp_path / "two" / "package.json").touch()
    monkeypatch.chdir(tmp_path)

    assert main(["one"]) == 0
    output = capsys.readouterr().out
    assert "one/package.json" in output
    assert "two/package.json" not in output


def test_main_path_to_file(tmp_path, capsys, monkeypatch):
    (tmp_path / "package.json").touch()
    (tmp_path / "requirements.txt").touch()
    monkeypatch.chdir(tmp_path)

    assert main(["--dry-run", "package.json"]) == 0
    output = capsys.readouterr().out
    assert "package.json" in output
    assert "requirements.txt" not in output


def test_main_path_does_not_exist(tmp_path, capsys, monkeypatch):
    monkeypatch.chdir(tmp_path)

    assert main(["missing"]) == 1
    assert "is not a file or directory" in capsys.readouterr().out


def test_main_duplicate_paths(tmp_path, capsys, monkeypatch):
    (tmp_path / "package.json").touch()
    monkeypatch.chdir(tmp_path)

    assert main(["package.json", "package.json", "."]) == 0
    output = capsys.readouterr().out
    # Deduplicated - mentioned once, not three times:
    assert output.count("package.json") == 1


def test_main_dry_run(tmp_path, capsys, monkeypatch):
    (tmp_path / "pyproject.toml").touch()
    monkeypatch.chdir(tmp_path)

    def fake_run(command, cwd):
        raise AssertionError("subprocess.run should not be called in dry run")

    monkeypatch.setattr(upd.upgrade.subprocess, "run", fake_run)

    assert main(["--dry-run"]) == 0
    assert "would run" in capsys.readouterr().out


def test_main_version(capsys):
    with pytest.raises(SystemExit) as excinfo:
        main(["--version"])
    assert excinfo.value.code == 0
    assert capsys.readouterr().out.strip() != ""


def test_main_help(capsys):
    with pytest.raises(SystemExit) as excinfo:
        main(["--help"])
    assert excinfo.value.code == 0
    captured = capsys.readouterr()
    assert "usage" in captured.out
    assert "--version" in captured.out
