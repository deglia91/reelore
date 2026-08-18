from pathlib import Path

from reelore.application import MediaTracker
from reelore.domain import EpisodeRef, LibraryStatus, MediaItem, MediaType
from reelore.infrastructure import SQLiteLibraryRepository


def test_media_tracker_persists_personal_state_and_episode_progress(tmp_path: Path) -> None:
    repository = SQLiteLibraryRepository(tmp_path / "reelore.db")
    repository.initialize()
    tracker = MediaTracker(repository)
    media = MediaItem(id="severance", title="Severance", media_type=MediaType.TV_SERIES)
    episode = EpisodeRef(1, 1)

    tracker.add_media(media, LibraryStatus.IN_PROGRESS)
    tracker.mark_episode_seen(media.id, episode)
    tracker.record_completion(media.id)
    tracker.record_completion(media.id)

    restored_state = repository.get_personal_state(media.id)
    restored_progress = repository.get_episode_progress(media.id)

    assert restored_state is not None
    assert restored_state.status is LibraryStatus.COMPLETED
    assert restored_state.completion_count == 2
    assert restored_state.rewatch_count == 1
    assert restored_progress.has_seen(episode)
