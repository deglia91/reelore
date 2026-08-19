import os
from pathlib import Path

from reelore.bootstrap import _load_env_file, build_app


def test_build_app_initializes_local_database(tmp_path: Path) -> None:
    database_path = tmp_path / "reelore.db"

    app = build_app(database_path)

    assert app.title == "Reelore"
    assert database_path.exists()


def test_load_env_file_sets_values_without_overriding_environment(tmp_path: Path) -> None:
    env_path = tmp_path / ".env"
    env_path.write_text(
        "# local configuration\n"
        "TMDB_API_TOKEN=from-file\n"
        "REELORE_DB_PATH='custom/reelore.db'\n",
        encoding="utf-8",
    )
    previous_token = os.environ.get("TMDB_API_TOKEN")
    previous_database = os.environ.get("REELORE_DB_PATH")
    os.environ["TMDB_API_TOKEN"] = "from-environment"
    os.environ.pop("REELORE_DB_PATH", None)
    try:
        _load_env_file(env_path)

        assert os.environ["TMDB_API_TOKEN"] == "from-environment"
        assert os.environ["REELORE_DB_PATH"] == "custom/reelore.db"
    finally:
        if previous_token is None:
            os.environ.pop("TMDB_API_TOKEN", None)
        else:
            os.environ["TMDB_API_TOKEN"] = previous_token
        if previous_database is None:
            os.environ.pop("REELORE_DB_PATH", None)
        else:
            os.environ["REELORE_DB_PATH"] = previous_database
