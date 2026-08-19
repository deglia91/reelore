from dataclasses import dataclass, field
from datetime import date

import pytest

from reelore.application import MediaNotFoundError, MediaTracker, TopTenService
from reelore.application.catalog import TVEpisodeMetadata, TVSeriesCatalog
from reelore.application.tracker import TVProgressTracker
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
    catalogs: dict[str, TVSeriesCatalog] = field(default_factory=dict)

    def save_media(self, media: MediaItem) -> None:
        self.media[media.id] = media

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

    def get_tv_series_catalog(self, provider_id: str) -> TVSeriesCatalog | None:
        return self.catalogs.get(provider_id)


def _severance(media_id: str = "severance") -> MediaItem:
    return MediaItem(id=media_id, title="Severance", media_type=MediaType.TV_SERIES)


def _catalog(status: str = "Running") -> TVSeriesCatalog:
    return TVSeriesCatalog(
        provider_id="1",
        title="Severance",
        summary=None,
        status=status,
        premiered=None,
        ended=None,
        image_url=None,
        episodes=(
            TVEpisodeMetadata("11", 1, 1, "Episode 1", airdate=date(2026, 1, 1)),
            TVEpisodeMetadata("12", 1, 2, "Episode 2", airdate=date(2026, 1, 8)),
        ),
    )


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


def test_top_ten_assigns_unique_rank_and_swaps_existing_occupant() -> None:
    repository = FakeLibraryRepository()
    tracker = MediaTracker(repository)
    first = MediaItem("first", "First", MediaType.TV_SERIES)
    second = MediaItem("second", "Second", MediaType.TV_SERIES)
    tracker.add_media(first)
    tracker.add_media(second)
    top_ten = TopTenService(repository)

    top_ten.assign(first.id, 2)
    top_ten.assign(second.id, 5)
    top_ten.assign(first.id, 5)

    assert repository.states[first.id].top_ten_rank == 5
    assert repository.states[second.id].top_ten_rank == 2


def test_top_ten_assigning_unranked_media_releases_occupied_rank() -> None:
    repository = FakeLibraryRepository()
    tracker = MediaTracker(repository)
    first = MediaItem("first", "First", MediaType.TV_SERIES)
    second = MediaItem("second", "Second", MediaType.TV_SERIES)
    tracker.add_media(first)
    tracker.add_media(second)
    top_ten = TopTenService(repository)

    top_ten.assign(first.id, 1)
    top_ten.assign(second.id, 1)

    assert repository.states[first.id].top_ten_rank is None
    assert repository.states[second.id].top_ten_rank == 1


def test_top_ten_remove_clears_rank_without_affecting_other_tracking() -> None:
    repository = FakeLibraryRepository()
    tracker = MediaTracker(repository)
    media = _severance()
    tracker.add_media(media, LibraryStatus.COMPLETED)
    tracker.record_completion(media.id)
    top_ten = TopTenService(repository)
    top_ten.assign(media.id, 3)

    removed = top_ten.remove(media.id)

    assert removed.top_ten_rank is None
    assert removed.status is LibraryStatus.COMPLETED
    assert removed.completion_count == 1


def test_tv_progress_starts_series_after_first_seen_episode() -> None:
    repository = FakeLibraryRepository()
    media = _severance("tvmaze:1")
    tracker = MediaTracker(repository)
    tracker.add_media(media)
    repository.catalogs["1"] = _catalog()
    progress_tracker = TVProgressTracker(tracker, repository, today=date(2026, 2, 1))

    progress_tracker.mark_episode_seen(media.id, EpisodeRef(1, 1))

    assert repository.states[media.id].status is LibraryStatus.IN_PROGRESS


def test_tv_progress_marks_running_series_up_to_date_when_available_episodes_are_seen() -> None:
    repository = FakeLibraryRepository()
    media = _severance("tvmaze:1")
    tracker = MediaTracker(repository)
    tracker.add_media(media)
    repository.catalogs["1"] = _catalog("Running")
    progress_tracker = TVProgressTracker(tracker, repository, today=date(2026, 2, 1))

    progress_tracker.mark_episode_seen(media.id, EpisodeRef(1, 1))
    progress_tracker.mark_episode_seen(media.id, EpisodeRef(1, 2))

    assert repository.states[media.id].status is LibraryStatus.UP_TO_DATE


def test_tv_progress_completes_ended_series_when_all_episodes_are_seen() -> None:
    repository = FakeLibraryRepository()
    media = _severance("tvmaze:1")
    tracker = MediaTracker(repository)
    tracker.add_media(media)
    repository.catalogs["1"] = _catalog("Ended")
    progress_tracker = TVProgressTracker(tracker, repository, today=date(2026, 2, 1))

    progress_tracker.mark_episode_seen(media.id, EpisodeRef(1, 1))
    progress_tracker.mark_episode_seen(media.id, EpisodeRef(1, 2))

    state = repository.states[media.id]
    assert state.status is LibraryStatus.COMPLETED
    assert state.completion_count == 1


def test_tv_progress_marking_completed_marks_all_catalog_episodes_seen() -> None:
    repository = FakeLibraryRepository()
    media = _severance("tvmaze:1")
    tracker = MediaTracker(repository)
    tracker.add_media(media)
    repository.catalogs["1"] = _catalog("Ended")
    progress_tracker = TVProgressTracker(tracker, repository)

    state = progress_tracker.change_status(media.id, LibraryStatus.COMPLETED)

    progress = repository.get_episode_progress(media.id)
    assert state.status is LibraryStatus.COMPLETED
    assert progress.seen_episodes == frozenset({EpisodeRef(1, 1), EpisodeRef(1, 2)})


def test_tv_progress_does_not_override_paused_or_dropped_status() -> None:
    for manual_status in (LibraryStatus.PAUSED, LibraryStatus.DROPPED):
        repository = FakeLibraryRepository()
        media = _severance("tvmaze:1")
        tracker = MediaTracker(repository)
        tracker.add_media(media, manual_status)
        repository.catalogs["1"] = _catalog("Ended")
        progress_tracker = TVProgressTracker(tracker, repository, today=date(2026, 2, 1))

        progress_tracker.mark_episode_seen(media.id, EpisodeRef(1, 1))
        progress_tracker.mark_episode_seen(media.id, EpisodeRef(1, 2))

        assert repository.states[media.id].status is manual_status


def test_tv_progress_reopens_completed_series_when_episode_becomes_unseen() -> None:
    repository = FakeLibraryRepository()
    media = _severance("tvmaze:1")
    tracker = MediaTracker(repository)
    tracker.add_media(media)
    repository.catalogs["1"] = _catalog("Ended")
    progress_tracker = TVProgressTracker(tracker, repository, today=date(2026, 2, 1))
    progress_tracker.mark_episode_seen(media.id, EpisodeRef(1, 1))
    progress_tracker.mark_episode_seen(media.id, EpisodeRef(1, 2))

    progress_tracker.mark_episode_unseen(media.id, EpisodeRef(1, 2))

    state = repository.states[media.id]
    assert state.status is LibraryStatus.IN_PROGRESS
    assert state.completion_count == 1


def test_tv_progress_reopens_up_to_date_series_when_episode_becomes_unseen() -> None:
    repository = FakeLibraryRepository()
    media = _severance("tvmaze:1")
    tracker = MediaTracker(repository)
    tracker.add_media(media)
    repository.catalogs["1"] = _catalog("Running")
    progress_tracker = TVProgressTracker(tracker, repository, today=date(2026, 2, 1))
    progress_tracker.mark_episode_seen(media.id, EpisodeRef(1, 1))
    progress_tracker.mark_episode_seen(media.id, EpisodeRef(1, 2))

    progress_tracker.mark_episode_unseen(media.id, EpisodeRef(1, 2))

    assert repository.states[media.id].status is LibraryStatus.IN_PROGRESS
