from dataclasses import dataclass, field
from datetime import UTC, datetime

import pytest

from reelore.application import MediaTracker
from reelore.application.tracker import TVProgressTracker
from reelore.domain import (
    EpisodeProgress,
    EpisodeRef,
    EpisodeWatch,
    LibraryStatus,
    MediaItem,
    MediaType,
    PersonalMediaState,
)


@dataclass
class FakeRepository:
    media: dict[str, MediaItem] = field(default_factory=dict)
    states: dict[str, PersonalMediaState] = field(default_factory=dict)
    progress: dict[str, EpisodeProgress] = field(default_factory=dict)
    watches: list[EpisodeWatch] = field(default_factory=list)

    def save_media(self, media: MediaItem) -> None:
        self.media[media.id] = media

    def remove_media(self, media_id: str) -> None:
        self.media.pop(media_id, None)
        self.states.pop(media_id, None)
        self.progress.pop(media_id, None)
        self.watches = [watch for watch in self.watches if watch.media_id != media_id]

    def get_media(self, media_id: str) -> MediaItem | None:
        return self.media.get(media_id)

    def list_media(self) -> tuple[MediaItem, ...]:
        return tuple(self.media.values())

    def save_personal_state(self, state: PersonalMediaState) -> None:
        self.states[state.media_id] = state

    def get_personal_state(self, media_id: str) -> PersonalMediaState | None:
        return self.states.get(media_id)

    def save_episode_progress(self, progress: EpisodeProgress) -> None:
        self.progress[progress.media_id] = progress

    def get_episode_progress(self, media_id: str) -> EpisodeProgress:
        return self.progress.get(media_id, EpisodeProgress(media_id=media_id))

    def get_tv_series_catalog(self, provider_id: str) -> None:
        return None

    def record_episode_watch(self, watch: EpisodeWatch) -> None:
        self.watches.append(watch)

    def list_episode_watches(self, media_id: str) -> tuple[EpisodeWatch, ...]:
        return tuple(watch for watch in self.watches if watch.media_id == media_id)

    def retract_latest_episode_watch(self, media_id: str, episode: EpisodeRef) -> bool:
        for index in range(len(self.watches) - 1, -1, -1):
            watch = self.watches[index]
            if watch.media_id == media_id and watch.episode == episode:
                del self.watches[index]
                return True
        return False


def test_explicit_rewatch_appends_another_watch_without_changing_progress() -> None:
    repository = FakeRepository()
    tracker = MediaTracker(repository, repository)
    media = MediaItem("tvmaze:1", "Example", MediaType.TV_SERIES)
    episode = EpisodeRef(1, 1)
    first_watch = datetime(2026, 8, 18, 20, 0, tzinfo=UTC)
    rewatch = datetime(2026, 8, 19, 20, 0, tzinfo=UTC)
    tracker.add_media(media, LibraryStatus.IN_PROGRESS)
    tracker.mark_episode_seen(media.id, episode, watched_at=first_watch)

    recorded = tracker.record_episode_rewatch(media.id, episode, watched_at=rewatch)

    assert recorded == EpisodeWatch(media.id, episode, rewatch)
    assert repository.watches == [
        EpisodeWatch(media.id, episode, first_watch),
        EpisodeWatch(media.id, episode, rewatch),
    ]
    assert repository.get_episode_progress(media.id).has_seen(episode)


def test_explicit_rewatch_requires_episode_to_have_been_seen() -> None:
    repository = FakeRepository()
    tracker = MediaTracker(repository, repository)
    media = MediaItem("tvmaze:1", "Example", MediaType.TV_SERIES)
    tracker.add_media(media)

    with pytest.raises(ValueError, match="cannot rewatch an unseen episode"):
        tracker.record_episode_rewatch(media.id, EpisodeRef(1, 1))


def test_tv_progress_rewatch_records_current_timestamp() -> None:
    repository = FakeRepository()
    media = MediaItem("tvmaze:1", "Example", MediaType.TV_SERIES)
    episode = EpisodeRef(1, 1)
    rewatch = datetime(2026, 8, 19, 21, 30, tzinfo=UTC)
    tracker = MediaTracker(repository, repository)
    tracker.add_media(media, LibraryStatus.IN_PROGRESS)
    tracker.mark_episode_seen(media.id, episode)
    progress_tracker = TVProgressTracker(tracker, repository, now=rewatch)

    progress_tracker.record_episode_rewatch(media.id, episode)

    assert repository.watches[-1] == EpisodeWatch(media.id, episode, rewatch)


def test_mark_episode_unseen_retracts_one_watch_at_a_time() -> None:
    repository = FakeRepository()
    tracker = MediaTracker(repository, repository)
    media = MediaItem("tvmaze:1", "Example", MediaType.TV_SERIES)
    episode = EpisodeRef(1, 1)
    tracker.add_media(media, LibraryStatus.IN_PROGRESS)
    tracker.mark_episode_seen(media.id, episode)
    tracker.record_episode_rewatch(media.id, episode)
    tracker.record_episode_rewatch(media.id, episode)

    first_step = tracker.mark_episode_unseen(media.id, episode)
    second_step = tracker.mark_episode_unseen(media.id, episode)
    final_step = tracker.mark_episode_unseen(media.id, episode)

    assert first_step.has_seen(episode)
    assert second_step.has_seen(episode)
    assert not final_step.has_seen(episode)
    assert repository.list_episode_watches(media.id) == ()


def test_unseen_episode_can_be_marked_seen_again_after_retraction() -> None:
    repository = FakeRepository()
    tracker = MediaTracker(repository, repository)
    media = MediaItem("tvmaze:1", "Example", MediaType.TV_SERIES)
    episode = EpisodeRef(1, 1)
    tracker.add_media(media, LibraryStatus.IN_PROGRESS)
    tracker.mark_episode_seen(media.id, episode)
    tracker.mark_episode_unseen(media.id, episode)

    tracker.mark_episode_seen(media.id, episode)

    assert tracker.get_episode_progress(media.id).has_seen(episode)
    assert len(repository.list_episode_watches(media.id)) == 1
