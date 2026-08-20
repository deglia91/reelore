from pathlib import Path
from stat import S_IXUSR


ROOT = Path(__file__).parents[2]


def test_makefile_exposes_lan_run_target() -> None:
    makefile = (ROOT / "Makefile").read_text()

    assert "run-lan:" in makefile
    assert "--host 0.0.0.0" in makefile
    assert "--port 8010" in makefile


def test_macos_launcher_uses_project_venv_and_lan_target() -> None:
    launcher = ROOT / "NextEp.command"
    content = launcher.read_text()

    assert content.startswith("#!/bin/zsh\n")
    assert '.venv/bin/uvicorn' in content
    assert "make run-lan" in content
    assert "http://127.0.0.1:8010" in content
    assert launcher.stat().st_mode & S_IXUSR
