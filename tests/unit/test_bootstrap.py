from pathlib import Path

from reelore.bootstrap import build_app


def test_build_app_initializes_local_database(tmp_path: Path) -> None:
    database_path = tmp_path / "reelore.db"

    app = build_app(database_path)

    assert app.title == "Reelore"
    assert database_path.exists()
