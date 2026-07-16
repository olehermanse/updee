from upd.main import main


def test_main_lists_upgrade_files(tmp_path, capsys, monkeypatch):
    (tmp_path / "package.json").touch()
    (tmp_path / "requirements.txt").touch()
    monkeypatch.chdir(tmp_path)

    assert main() == 0
    captured = capsys.readouterr()
    assert captured.out == "package.json\nrequirements.txt\n"


def test_main_with_no_upgrade_files(tmp_path, capsys, monkeypatch):
    monkeypatch.chdir(tmp_path)

    assert main() == 1
    captured = capsys.readouterr()
    assert captured.out == "No files to upgrade found\n"
