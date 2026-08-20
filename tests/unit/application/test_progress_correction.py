from dataclasses import dataclass, field
from datetime import date

import pytest

from reelore.application.catalog import TVEpisodeMetadata, TVSeriesCatalog
from reelore.application.tracker import MediaTracker, TVProgressTracker
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
class FakeProgressRepository:
    media: dict[str, MediaItem] = field(default_factory=dict)
    states: dict[str, PersonalMediaState] = field(default_factory=dict)
    progress: dict[str, EpisodeProgress] = field(default_factory=dict)
    catalogs: dict[str, TVSeriesCatalog] = field(default_factory=dict)
    watches: list[EpisodeWatch] = field(default_factory=list)

    def save_media(self, media: MediaItem) -> None:
        self.media[media.id] = media

    def remove_media(self, media_id: str) -> None:
        self.media.pop(media_id, None)

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
        return self.progress.get(media_id, EpisodeProgress(media_id))

    def get_tv_series_catalog(self, provider_id: str) -> TVSeriesCatalog | None:
        return self.catalogs.get(provider_id)

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


def _catalog() -> TVSeriesCatalog:
    return TVSeriesCatalog(
        provider_id="1",
        title="Example",
        summary=None,
        status="Running",
        premiered=None,
        ended=None,
        image_url=None,
        episodes=(
            TVEpisodeMetadata("11", 1, 1, "One", airdate=date(2026, 1, 1)),
            TVEpisodeMetadata("12", 1, 2, "Two", airdate=date(2026, 1, 8)),
            TVEpisodeMetadata("21", 2, 1, "Three", airdate=date(2026, 1, 15)),
            TVEpisodeMetadata("22", 2, 2, "Future", airdate=date(2026, 9, 1)),
        ),
    )


def _tracker() -> tuple[FakeProgressRepository, TVProgressTracker]:
    repository = FakeProgressRepository()
    media = MediaItem("tvmaze:1", "Example", MediaType.TV_SERIES)
    tracker = MediaTracker(repository, repository)
    tracker.add_media(media)
    repository.catalogs["1"] = _catalog()
    return repository, TVProgressTracker(tracker, repository, today=date(2026, 8, 20))


def test_progress_correction_marks_missing_episodes_through_target_without_rewatching() -> None:
    repository, tracker = _tracker()
    first = EpisodeRef(1, 1)
    target = EpisodeRef(2, 1)
    tracker.mark_episode_seen("tvmaze:1", first)
    tracker.record_episode_rewatch("tvmaze:1", first)

    progress = tracker.mark_episodes_through("tvmaze:1", target)

    assert progress.seen_episodes == frozenset(
        {EpisodeRef(1, 1), EpisodeRef(1, 2), EpisodeRef(2, 1)}
    )
    assert len([watch for watch in repository.watches if watch.episode == first]) == 2
    assert [watch.watched_at for watch in repository.watches if watch.episode != first] == [
        None,
        None,
    ]
    assert repository.states["tvmaze:1"].status is LibraryStatus.UP_TO_DATE


def test_progress_correction_rejects_future_target() -> None:
    _repository, tracker = _tracker()

    with pytest.raises(ValueError, match="future episode"):
        tracker.mark_episodes_through("tvmaze:1", EpisodeRef(2, 2))


def test_direct_episode_tracking_rejects_future_episode() -> None:
    repository, tracker = _tracker()

    with pytest.raises(ValueError, match="future episode"):
        tracker.mark_episode_seen("tvmaze:1", EpisodeRef(2, 2))

    assert repository.get_episode_progress("tvmaze:1").seen_count == 0
    assert repository.watches == []
