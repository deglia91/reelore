from pathlib import Path

from reelore.application import LibraryRepository
from reelore.domain import (
    EpisodeProgress,
    EpisodeRef,
    LibraryStatus,
    MediaItem,
    MediaType,
    PersonalMediaState,
)
from reelore.infrastructure import SQLiteLibraryRepository


def _repository(database_path: Path) -> SQLiteLibraryRepository:
    repository = SQLiteLibraryRepository(database_path)
    repository.initialize()
    return repository


def _accept_repository(repository: LibraryRepository) -> None:
    assert repository is not None


def test_sqlite_repository_satisfies_library_port(tmp_path: Path) -> None:
    repository = _repository(tmp_path / "reelore.db")

    _accept_repository(repository)


def test_sqlite_repository_round_trips_media_and_personal_state(tmp_path: Path) -> None:
    repository = _repository(tmp_path / "reelore.db")
    media = MediaItem(id="severance", title="Severance", media_type=MediaType.TV_SERIES)
    state = PersonalMediaState(
        media_id=media.id,
        status=LibraryStatus.IN_PROGRESS,
        completion_count=2,
        top_ten_rank=3,
    )

    repository.save_media(media)
    repository.save_personal_state(state)

    assert repository.get_media(media.id) == media
    assert repository.get_personal_state(media.id) == state


def test_sqlite_repository_lists_media_by_title(tmp_path: Path) -> None:
    repository = _repository(tmp_path / "reelore.db")
    severance = MediaItem(id="severance", title="Severance", media_type=MediaType.TV_SERIES)
    bear = MediaItem(id="the-bear", title="The Bear", media_type=MediaType.TV_SERIES)

    repository.save_media(severance)
    repository.save_media(bear)

    assert repository.list_media() == (severance, bear)


def test_sqlite_repository_round_trips_episode_progress(tmp_path: Path) -> None:
    repository = _repository(tmp_path / "reelore.db")
    media = MediaItem(id="severance", title="Severance", media_type=MediaType.TV_SERIES)
    progress = (
        EpisodeProgress(media_id=media.id).mark_seen(EpisodeRef(1, 1)).mark_seen(EpisodeRef(1, 2))
    )

    repository.save_media(media)
    repository.save_episode_progress(progress)

    assert repository.get_episode_progress(media.id) == progress


def test_sqlite_episode_progress_replaces_previous_snapshot(tmp_path: Path) -> None:
    repository = _repository(tmp_path / "reelore.db")
    media = MediaItem(id="severance", title="Severance", media_type=MediaType.TV_SERIES)
    repository.save_media(media)
    repository.save_episode_progress(
        EpisodeProgress(media_id=media.id).mark_seen(EpisodeRef(1, 1)).mark_seen(EpisodeRef(1, 2))
    )

    repository.save_episode_progress(EpisodeProgress(media_id=media.id).mark_seen(EpisodeRef(1, 1)))

    restored = repository.get_episode_progress(media.id)
    assert restored.seen_episodes == frozenset({EpisodeRef(1, 1)})
