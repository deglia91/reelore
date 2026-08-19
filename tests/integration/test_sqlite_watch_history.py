from datetime import UTC, datetime
from pathlib import Path

from reelore.application import WatchHistoryRepository
from reelore.domain import EpisodeProgress, EpisodeRef, EpisodeWatch, MediaItem, MediaType
from reelore.infrastructure import SQLiteLibraryRepository, SQLiteWatchHistoryRepository


def _library(database_path: Path) -> SQLiteLibraryRepository:
    repository = SQLiteLibraryRepository(database_path)
    repository.initialize()
    return repository


def _history(database_path: Path) -> SQLiteWatchHistoryRepository:
    repository = SQLiteWatchHistoryRepository(database_path)
    repository.initialize()
    return repository


def _accept_repository(repository: WatchHistoryRepository) -> None:
    assert repository is not None


def test_sqlite_watch_history_satisfies_port_and_preserves_multiple_watches(tmp_path: Path) -> None:
    database_path = tmp_path / "reelore.db"
    library = _library(database_path)
    media = MediaItem("tvmaze:1", "Severance", MediaType.TV_SERIES)
    library.save_media(media)
    history = _history(database_path)
    _accept_repository(history)
    episode = EpisodeRef(1, 1)
    first = EpisodeWatch(media.id, episode, datetime(2026, 8, 18, 20, 0, tzinfo=UTC))
    second = EpisodeWatch(media.id, episode, datetime(2026, 8, 19, 20, 0, tzinfo=UTC))

    history.record_episode_watch(first)
    history.record_episode_watch(second)

    assert history.list_episode_watches(media.id) == (first, second)


def test_sqlite_watch_history_migrates_legacy_seen_episode_without_fake_timestamp(
    tmp_path: Path,
) -> None:
    database_path = tmp_path / "reelore.db"
    library = _library(database_path)
    media = MediaItem("tvmaze:1", "Severance", MediaType.TV_SERIES)
    library.save_media(media)
    episode = EpisodeRef(1, 1)
    library.save_episode_progress(EpisodeProgress(media.id).mark_seen(episode))

    history = _history(database_path)

    assert history.list_episode_watches(media.id) == (EpisodeWatch(media.id, episode),)
