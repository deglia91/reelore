from dataclasses import dataclass, field

from reelore.application import MediaTracker
from reelore.domain import EpisodeProgress, LibraryStatus, MediaItem, MediaType, PersonalMediaState


@dataclass
class CompletionStore:
    media: dict[str, MediaItem] = field(default_factory=dict)
    states: dict[str, PersonalMediaState] = field(default_factory=dict)

    def save_media(self, media: MediaItem) -> None:
        self.media[media.id] = media

    def get_media(self, media_id: str) -> MediaItem | None:
        return self.media.get(media_id)

    def list_media(self) -> tuple[MediaItem, ...]:
        return tuple(self.media.values())

    def remove_media(self, media_id: str) -> None:
        self.media.pop(media_id, None)
        self.states.pop(media_id, None)

    def save_personal_state(self, state: PersonalMediaState) -> None:
        self.states[state.media_id] = state

    def get_personal_state(self, media_id: str) -> PersonalMediaState | None:
        return self.states.get(media_id)

    def save_episode_progress(self, progress: EpisodeProgress) -> None:
        pass

    def get_episode_progress(self, media_id: str) -> EpisodeProgress:
        return EpisodeProgress(media_id)


def test_manual_completed_status_records_first_completion() -> None:
    store = CompletionStore()
    tracker = MediaTracker(store)
    media = MediaItem("series:1", "Series", MediaType.TV_SERIES)
    tracker.add_media(media, LibraryStatus.IN_PROGRESS)

    state = tracker.change_status(media.id, LibraryStatus.COMPLETED)

    assert state.status is LibraryStatus.COMPLETED
    assert state.completion_count == 1
    assert state.rewatch_count == 0


def test_reselecting_completed_status_does_not_create_rewatch() -> None:
    store = CompletionStore()
    tracker = MediaTracker(store)
    media = MediaItem("series:1", "Series", MediaType.TV_SERIES)
    tracker.add_media(media, LibraryStatus.IN_PROGRESS)
    tracker.change_status(media.id, LibraryStatus.COMPLETED)

    state = tracker.change_status(media.id, LibraryStatus.COMPLETED)

    assert state.completion_count == 1
    assert state.rewatch_count == 0
