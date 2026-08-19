"""Application use cases for the personal media tracker."""

from datetime import date
from typing import ClassVar, Protocol

from reelore.application.catalog import TVSeriesCatalog
from reelore.application.library import LibraryRepository
from reelore.domain import EpisodeProgress, EpisodeRef, LibraryStatus, MediaItem, PersonalMediaState


class MediaNotFoundError(LookupError):
    """Raised when a tracking operation targets media outside the library."""


class MediaTracker:
    """Coordinate personal tracking use cases through the library repository port."""

    def __init__(self, repository: LibraryRepository) -> None:
        self._repository = repository

    def add_media(self, media: MediaItem, status: LibraryStatus = LibraryStatus.PLANNED) -> None:
        self._repository.save_media(media)
        if self._repository.get_personal_state(media.id) is None:
            self._repository.save_personal_state(
                PersonalMediaState(media_id=media.id, status=status)
            )

    def change_status(self, media_id: str, status: LibraryStatus) -> PersonalMediaState:
        state = self._require_state(media_id).change_status(status)
        self._repository.save_personal_state(state)
        return state

    def record_completion(self, media_id: str) -> PersonalMediaState:
        state = self._require_state(media_id).record_completion()
        self._repository.save_personal_state(state)
        return state

    def mark_episode_seen(self, media_id: str, episode: EpisodeRef) -> EpisodeProgress:
        self._require_media(media_id)
        progress = self._repository.get_episode_progress(media_id).mark_seen(episode)
        self._repository.save_episode_progress(progress)
        return progress

    def mark_episode_unseen(self, media_id: str, episode: EpisodeRef) -> EpisodeProgress:
        self._require_media(media_id)
        progress = self._repository.get_episode_progress(media_id).mark_unseen(episode)
        self._repository.save_episode_progress(progress)
        return progress

    def get_episode_progress(self, media_id: str) -> EpisodeProgress:
        self._require_media(media_id)
        return self._repository.get_episode_progress(media_id)

    def _require_media(self, media_id: str) -> MediaItem:
        media = self._repository.get_media(media_id)
        if media is None:
            raise MediaNotFoundError(media_id)
        return media

    def _require_state(self, media_id: str) -> PersonalMediaState:
        self._require_media(media_id)
        state = self._repository.get_personal_state(media_id)
        if state is None:
            raise MediaNotFoundError(media_id)
        return state


class TopTenStore(Protocol):
    def list_media(self) -> tuple[MediaItem, ...]: ...

    def get_personal_state(self, media_id: str) -> PersonalMediaState | None: ...

    def save_personal_state(self, state: PersonalMediaState) -> None: ...


class TopTenService:
    """Manage a unique personal top-ten ranking for library media."""

    def __init__(self, store: TopTenStore) -> None:
        self._store = store

    def assign(self, media_id: str, rank: int) -> PersonalMediaState:
        state = self._require_state(media_id)
        previous_rank = state.top_ten_rank
        occupant = self._state_at_rank(rank, excluding=media_id)
        if occupant is not None:
            self._store.save_personal_state(occupant.rank_in_top_ten(previous_rank))
        ranked = state.rank_in_top_ten(rank)
        self._store.save_personal_state(ranked)
        return ranked

    def remove(self, media_id: str) -> PersonalMediaState:
        state = self._require_state(media_id).rank_in_top_ten(None)
        self._store.save_personal_state(state)
        return state

    def _state_at_rank(
        self,
        rank: int,
        *,
        excluding: str,
    ) -> PersonalMediaState | None:
        for media in self._store.list_media():
            if media.id == excluding:
                continue
            state = self._store.get_personal_state(media.id)
            if state is not None and state.top_ten_rank == rank:
                return state
        return None

    def _require_state(self, media_id: str) -> PersonalMediaState:
        state = self._store.get_personal_state(media_id)
        if state is None:
            raise MediaNotFoundError(media_id)
        return state


class TVProgressStore(Protocol):
    def get_personal_state(self, media_id: str) -> PersonalMediaState | None: ...

    def get_tv_series_catalog(self, provider_id: str) -> TVSeriesCatalog | None: ...


class TVProgressTracker:
    """Keep personal TV status aligned with episode progress."""

    _MANUAL_STATUSES: ClassVar[set[LibraryStatus]] = {
        LibraryStatus.PAUSED,
        LibraryStatus.DROPPED,
    }

    def __init__(
        self,
        tracker: MediaTracker,
        store: TVProgressStore,
        *,
        today: date | None = None,
    ) -> None:
        self._tracker = tracker
        self._store = store
        self._today = today

    def change_status(self, media_id: str, status: LibraryStatus) -> PersonalMediaState:
        if status is LibraryStatus.COMPLETED:
            catalog = self._catalog_for(media_id)
            if catalog is not None:
                for episode in catalog.episodes:
                    self._tracker.mark_episode_seen(
                        media_id,
                        EpisodeRef(episode.season_number, episode.episode_number),
                    )
        return self._tracker.change_status(media_id, status)

    def record_completion(self, media_id: str) -> PersonalMediaState:
        return self._tracker.record_completion(media_id)

    def mark_episode_seen(self, media_id: str, episode: EpisodeRef) -> EpisodeProgress:
        progress = self._tracker.mark_episode_seen(media_id, episode)
        self._sync_after_seen(media_id, progress)
        return progress

    def mark_episode_unseen(self, media_id: str, episode: EpisodeRef) -> EpisodeProgress:
        progress = self._tracker.mark_episode_unseen(media_id, episode)
        state = self._store.get_personal_state(media_id)
        if state is not None and state.status in {
            LibraryStatus.UP_TO_DATE,
            LibraryStatus.COMPLETED,
        }:
            self._tracker.change_status(media_id, LibraryStatus.IN_PROGRESS)
        return progress

    def _sync_after_seen(self, media_id: str, progress: EpisodeProgress) -> None:
        state = self._store.get_personal_state(media_id)
        if state is None or state.status in self._MANUAL_STATUSES:
            return
        if state.status is LibraryStatus.PLANNED:
            state = self._tracker.change_status(media_id, LibraryStatus.IN_PROGRESS)

        catalog = self._catalog_for(media_id)
        if catalog is None or state.status is LibraryStatus.COMPLETED:
            return
        available = tuple(
            episode
            for episode in catalog.episodes
            if episode.airdate is None or episode.airdate <= (self._today or date.today())
        )
        if not available:
            return
        all_seen = all(
            progress.has_seen(EpisodeRef(episode.season_number, episode.episode_number))
            for episode in available
        )
        if not all_seen:
            if state.status is LibraryStatus.UP_TO_DATE:
                self._tracker.change_status(media_id, LibraryStatus.IN_PROGRESS)
            return

        series_ended = (catalog.status or "").casefold() == "ended"
        all_catalog_episodes_available = len(available) == len(catalog.episodes)
        if series_ended and all_catalog_episodes_available:
            self._tracker.record_completion(media_id)
            return
        if not series_ended:
            self._tracker.change_status(media_id, LibraryStatus.UP_TO_DATE)

    def _catalog_for(self, media_id: str) -> TVSeriesCatalog | None:
        _prefix, separator, provider_id = media_id.partition(":")
        if not separator or not provider_id:
            return None
        return self._store.get_tv_series_catalog(provider_id)
