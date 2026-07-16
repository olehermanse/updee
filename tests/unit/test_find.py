from pathlib import Path

from updee.find import find_upgrade_files


def test_finds_upgrade_files(tmp_path):
    (tmp_path / "package.json").touch()
    (tmp_path / "package-lock.json").touch()
    (tmp_path / "requirements.txt").touch()
    (tmp_path / "pyproject.toml").touch()
    (tmp_path / "README.md").touch()

    found = find_upgrade_files(tmp_path)
    assert [f.name for f in found] == [
        "package-lock.json",
        "package.json",
        "pyproject.toml",
        "requirements.txt",
    ]


def test_finds_files_in_subdirectories(tmp_path):
    subdir = tmp_path / "subproject"
    subdir.mkdir()
    (subdir / "package.json").touch()

    found = find_upgrade_files(tmp_path)
    assert found == [subdir / "package.json"]


def test_skips_hidden_and_vendored_directories(tmp_path):
    for name in (".git", ".venv", "node_modules", "__pycache__"):
        directory = tmp_path / name
        directory.mkdir()
        (directory / "package.json").touch()

    assert find_upgrade_files(tmp_path) == []


def test_finds_github_workflows(tmp_path):
    workflows = tmp_path / ".github" / "workflows"
    workflows.mkdir(parents=True)
    (workflows / "ci.yml").touch()
    (workflows / "publish.yaml").touch()
    (workflows / "README.md").touch()
    (tmp_path / ".github" / "dependabot.yml").touch()
    (tmp_path / "other.yml").touch()

    found = find_upgrade_files(tmp_path)
    assert found == [workflows / "ci.yml", workflows / "publish.yaml"]


def test_empty_directory(tmp_path):
    assert find_upgrade_files(tmp_path) == []


def test_returns_paths_relative_to_given_root(tmp_path, monkeypatch):
    (tmp_path / "requirements.txt").touch()
    monkeypatch.chdir(tmp_path)

    assert find_upgrade_files(Path(".")) == [Path("requirements.txt")]
