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

    assert main() == 0
    assert len(calls) == 1
    assert calls[0][0] == ["uv", "lock", "--upgrade"]


def test_main_skips_unsupported_files(tmp_path, capsys, monkeypatch):
    (tmp_path / "package.json").touch()
    monkeypatch.chdir(tmp_path)

    assert main() == 0
    assert "skipping" in capsys.readouterr().out


def test_main_with_no_upgrade_files(tmp_path, capsys, monkeypatch):
    monkeypatch.chdir(tmp_path)

    assert main() == 1
    captured = capsys.readouterr()
    assert captured.out == "No files to upgrade found\n"
