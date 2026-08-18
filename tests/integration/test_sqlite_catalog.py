from datetime import date
from pathlib import Path

from reelore.application import TVCastMember, TVCatalogStore, TVEpisodeMetadata, TVSeriesCatalog
from reelore.infrastructure import SQLiteLibraryRepository


def _repository(database_path: Path) -> SQLiteLibraryRepository:
    repository = SQLiteLibraryRepository(database_path)
    repository.initialize()
    return repository


def _accept_catalog_store(store: TVCatalogStore) -> None:
    assert store is not None


def test_sqlite_repository_round_trips_tv_catalog(tmp_path: Path) -> None:
    repository = _repository(tmp_path / "reelore.db")
    _accept_catalog_store(repository)
    catalog = TVSeriesCatalog(
        provider_id="16740",
        title="Severance",
        summary="Office workers undergo a severance procedure.",
        status="Running",
        premiered=date(2022, 2, 18),
        ended=None,
        image_url="https://img.example/show.jpg",
        episodes=(
            TVEpisodeMetadata(
                provider_id="2001",
                season_number=1,
                episode_number=1,
                title="Good News About Hell",
                airdate=date(2022, 2, 18),
                summary="Mark returns to work.",
                image_url="https://img.example/e1.jpg",
            ),
        ),
        cast=(TVCastMember("Adam Scott", "Mark Scout", "https://img.example/adam.jpg"),),
    )

    repository.save_tv_series_catalog(catalog)

    assert repository.get_tv_series_catalog("16740") == catalog


def test_sqlite_catalog_refresh_replaces_episode_and_cast_snapshots(tmp_path: Path) -> None:
    repository = _repository(tmp_path / "reelore.db")
    original = TVSeriesCatalog(
        provider_id="16740",
        title="Severance",
        summary=None,
        status="Running",
        premiered=None,
        ended=None,
        image_url=None,
        episodes=(TVEpisodeMetadata("2001", 1, 1, "Episode 1"),),
        cast=(TVCastMember("Adam Scott", "Mark Scout"),),
    )
    refreshed = TVSeriesCatalog(
        provider_id="16740",
        title="Severance",
        summary=None,
        status="Running",
        premiered=None,
        ended=None,
        image_url=None,
        episodes=(TVEpisodeMetadata("2002", 1, 2, "Episode 2"),),
        cast=(TVCastMember("Britt Lower", "Helly R."),),
    )

    repository.save_tv_series_catalog(original)
    repository.save_tv_series_catalog(refreshed)

    assert repository.get_tv_series_catalog("16740") == refreshed
