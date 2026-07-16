from upd.main import main


def test_main(capsys):
    assert main() == 0
    captured = capsys.readouterr()
    assert captured.out == "Hello, world!\n"
