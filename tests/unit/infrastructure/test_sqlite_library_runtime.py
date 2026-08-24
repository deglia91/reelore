import sqlite3
from pathlib import Path

from reelore.application import TVEpisodeMetadata, TVSeriesCatalog
from reelore.infrastructure import SQLiteLibraryRepository


def test_sqlite_catalog_round_trips_episode_runtime(tmp_path: Path) -> None:
    database_path = tmp_path / "reelore.db"
    repository = SQLiteLibraryRepository(database_path)
    repository.initialize()
    repository.save_tv_series_catalog(
        TVSeriesCatalog(
            provider_id="1",
            title="Example",
            summary=None,
            status="Running",
            premiered=None,
            ended=None,
            image_url=None,
            episodes=(
                TVEpisodeMetadata(
                    "11",
                    1,
                    1,
                    "Pilot",
                    runtime_minutes=52,
                ),
            ),
        )
    )

    catalog = repository.get_tv_series_catalog("1")

    assert catalog is not None
    assert catalog.episodes[0].runtime_minutes == 52


def test_sqlite_initialize_migrates_legacy_episode_catalog(tmp_path: Path) -> None:
    database_path = tmp_path / "legacy.db"
    with sqlite3.connect(database_path) as connection:
        connection.execute(
            """
            CREATE TABLE tv_episode_catalog (
                series_provider_id TEXT NOT NULL,
                provider_id TEXT NOT NULL,
                season_number INTEGER NOT NULL,
                episode_number INTEGER NOT NULL,
                title TEXT NOT NULL,
                airdate TEXT,
                summary TEXT,
                image_url TEXT,
                PRIMARY KEY (series_provider_id, provider_id)
            )
            """
        )

    SQLiteLibraryRepository(database_path).initialize()

    with sqlite3.connect(database_path) as connection:
        columns = {
            str(row[1]) for row in connection.execute("PRAGMA table_info(tv_episode_catalog)")
        }

    assert "runtime_minutes" in columns
