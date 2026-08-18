from dataclasses import dataclass, field

import pytest

from reelore.application import MediaNotFoundError, MediaTracker
from reelore.domain import (
    EpisodeProgress,
    EpisodeRef,
    LibraryStatus,
    MediaItem,
    MediaType,
    PersonalMediaState,
)


@dataclass
class FakeLibraryRepository:
    media: dict[str, MediaItem] = field(default_factory=dict)
    states: dict[str, PersonalMediaState] = field(default_factory=dict)
    progress: dict[str, EpisodeProgress] = field(default_factory=dict)

    def save_media(self, media: MediaItem) -> None:
        self.media[media.id] = media

    def get_media(self, media_id: str) -> MediaItem | None:
        return self.media.get(media_id)

    def save_personal_state(self, state: PersonalMediaState) -> None:
        self.states[state.media_id] = state

    def get_personal_state(self, media_id: str) -> PersonalMediaState | None:
        return self.states.get(media_id)

    def save_episode_progress(self, progress: EpisodeProgress) -> None:
        self.progress[progress.media_id] = progress

    def get_episode_progress(self, media_id: str) -> EpisodeProgress:
        return self.progress.get(media_id, EpisodeProgress(media_id=media_id))


def _severance() -> MediaItem:
    return MediaItem(id="severance", title="Severance", media_type=MediaType.TV_SERIES)


def test_add_media_creates_personal_state_without_resetting_existing_tracking() -> None:
    repository = FakeLibraryRepository()
    tracker = MediaTracker(repository)
    media = _severance()

    tracker.add_media(media, LibraryStatus.IN_PROGRESS)
    tracker.record_completion(media.id)
    tracker.add_media(media, LibraryStatus.PLANNED)

    assert repository.states[media.id].status is LibraryStatus.COMPLETED
    assert repository.states[media.id].completion_count == 1


def test_change_status_and_record_completion_preserve_tracking_history() -> None:
    repository = FakeLibraryRepository()
    tracker = MediaTracker(repository)
    media = _severance()
    tracker.add_media(media)

    tracker.change_status(media.id, LibraryStatus.IN_PROGRESS)
    completed = tracker.record_completion(media.id)
    rewatched = tracker.record_completion(media.id)

    assert completed.completion_count == 1
    assert rewatched.completion_count == 2
    assert rewatched.rewatch_count == 1


def test_episode_seen_and_unseen_are_idempotent() -> None:
    repository = FakeLibraryRepository()
    tracker = MediaTracker(repository)
    media = _severance()
    episode = EpisodeRef(1, 1)
    tracker.add_media(media)

    tracker.mark_episode_seen(media.id, episode)
    tracker.mark_episode_seen(media.id, episode)
    progress = tracker.mark_episode_unseen(media.id, episode)
    progress = tracker.mark_episode_unseen(media.id, episode)

    assert progress.seen_count == 0


def test_tracking_unknown_media_fails_explicitly() -> None:
    tracker = MediaTracker(FakeLibraryRepository())

    with pytest.raises(MediaNotFoundError, match="missing"):
        tracker.change_status("missing", LibraryStatus.IN_PROGRESS)

    with pytest.raises(MediaNotFoundError, match="missing"):
        tracker.mark_episode_seen("missing", EpisodeRef(1, 1))
