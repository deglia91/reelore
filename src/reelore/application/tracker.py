"""Application use cases for the personal media tracker."""

from datetime import UTC, date, datetime
from typing import ClassVar, Protocol

from reelore.application.catalog import TVSeriesCatalog
from reelore.application.library import LibraryRepository
from reelore.application.watch_history import WatchHistoryRepository
from reelore.domain import (
    EpisodeProgress,
    EpisodeRef,
    EpisodeWatch,
    LibraryStatus,
    MediaItem,
    PersonalMediaState,
)


class MediaNotFoundError(LookupError):
    """Raised when a tracking operation targets media outside the library."""


class MediaTracker:
    """Coordinate personal tracking use cases through the library repository port."""

    def __init__(
        self,
        repository: LibraryRepository,
        watch_history: WatchHistoryRepository | None = None,
    ) -> None:
        self._repository = repository
        self._watch_history = watch_history

    def add_media(self, media: MediaItem, status: LibraryStatus = LibraryStatus.PLANNED) -> None:
        self._repository.save_media(media)
        if self._repository.get_personal_state(media.id) is None:
            self._repository.save_personal_state(
                PersonalMediaState(media_id=media.id, status=status)
            )

    def remove_media(self, media_id: str) -> MediaItem:
        media = self._require_media(media_id)
        self._repository.remove_media(media_id)
        return media

    def change_status(self, media_id: str, status: LibraryStatus) -> PersonalMediaState:
        state = self._require_state(media_id).change_status(status)
        self._repository.save_personal_state(state)
        return state

    def record_completion(self, media_id: str) -> PersonalMediaState:
        state = self._require_state(media_id).record_completion()
        self._repository.save_personal_state(state)
        return state

    def mark_episode_seen(
        self,
        media_id: str,
        episode: EpisodeRef,
        *,
        watched_at: datetime | None = None,
    ) -> EpisodeProgress:
        self._require_media(media_id)
        self._record_first_watch(media_id, episode, watched_at)
        progress = self._repository.get_episode_progress(media_id).mark_seen(episode)
        self._repository.save_episode_progress(progress)
        return progress

    def record_episode_rewatch(
        self,
        media_id: str,
        episode: EpisodeRef,
        *,
        watched_at: datetime | None = None,
    ) -> EpisodeWatch:
        self._require_media(media_id)
        progress = self._repository.get_episode_progress(media_id)
        if not progress.has_seen(episode):
            raise ValueError("cannot rewatch an unseen episode")
        if self._watch_history is None:
            raise RuntimeError("watch history is not configured")
        watch = EpisodeWatch(media_id=media_id, episode=episode, watched_at=watched_at)
        self._watch_history.record_episode_watch(watch)
        return watch

    def mark_episode_unseen(self, media_id: str, episode: EpisodeRef) -> EpisodeProgress:
        self._require_media(media_id)
        progress = self._repository.get_episode_progress(media_id)
        if not progress.has_seen(episode):
            return progress
        if self._watch_history is not None:
            watches = tuple(
                watch
                for watch in self._watch_history.list_episode_watches(media_id)
                if watch.episode == episode
            )
            if watches:
                self._watch_history.retract_latest_episode_watch(media_id, episode)
                if len(watches) > 1:
                    return progress
        progress = progress.mark_unseen(episode)
        self._repository.save_episode_progress(progress)
        return progress

    def get_episode_progress(self, media_id: str) -> EpisodeProgress:
        self._require_media(media_id)
        return self._repository.get_episode_progress(media_id)

    def _record_first_watch(
        self,
        media_id: str,
        episode: EpisodeRef,
        watched_at: datetime | None,
    ) -> None:
        if self._watch_history is None:
            return
        existing = self._watch_history.list_episode_watches(media_id)
        if any(watch.episode == episode for watch in existing):
            return
        self._watch_history.record_episode_watch(
            EpisodeWatch(media_id=media_id, episode=episode, watched_at=watched_at)
        )

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
        now: datetime | None = None,
    ) -> None:
        self._tracker = tracker
        self._store = store
        self._today = today
        self._now = now

    def remove_media(self, media_id: str) -> MediaItem:
        return self._tracker.remove_media(media_id)

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
        self._reject_future_episode(media_id, episode)
        watched_at = self._now or datetime.now(UTC)
        progress = self._tracker.mark_episode_seen(media_id, episode, watched_at=watched_at)
        self._sync_after_seen(media_id, progress)
        return progress

    def mark_season_seen(self, media_id: str, season_number: int) -> EpisodeProgress:
        catalog = self._catalog_for(media_id)
        if catalog is None:
            return self._tracker.get_episode_progress(media_id)
        today = self._today or date.today()
        progress = self._tracker.get_episode_progress(media_id)
        for episode in catalog.episodes:
            if episode.season_number != season_number:
                continue
            if episode.airdate is not None and episode.airdate > today:
                continue
            reference = EpisodeRef(episode.season_number, episode.episode_number)
            if progress.has_seen(reference):
                continue
            progress = self.mark_episode_seen(media_id, reference)
        return progress

    def mark_episodes_through(self, media_id: str, target: EpisodeRef) -> EpisodeProgress:
        catalog = self._catalog_for(media_id)
        if catalog is None:
            return self._tracker.get_episode_progress(media_id)
        today = self._today or date.today()
        ordered = sorted(
            catalog.episodes,
            key=lambda episode: (episode.season_number, episode.episode_number),
        )
        target_episode = next(
            (
                episode
                for episode in ordered
                if episode.season_number == target.season_number
                and episode.episode_number == target.episode_number
            ),
            None,
        )
        if target_episode is None:
            raise ValueError("episode not found in catalog")
        if target_episode.airdate is not None and target_episode.airdate > today:
            raise ValueError("cannot correct progress through a future episode")

        progress = self._tracker.get_episode_progress(media_id)
        for episode in ordered:
            reference = EpisodeRef(episode.season_number, episode.episode_number)
            if reference > target:
                break
            if episode.airdate is not None and episode.airdate > today:
                continue
            if progress.has_seen(reference):
                continue
            progress = self._tracker.mark_episode_seen(media_id, reference, watched_at=None)
        self._sync_after_seen(media_id, progress)
        return progress

    def record_episode_rewatch(self, media_id: str, episode: EpisodeRef) -> EpisodeWatch:
        watched_at = self._now or datetime.now(UTC)
        return self._tracker.record_episode_rewatch(media_id, episode, watched_at=watched_at)

    def mark_episode_unseen(self, media_id: str, episode: EpisodeRef) -> EpisodeProgress:
        progress = self._tracker.mark_episode_unseen(media_id, episode)
        if progress.has_seen(episode):
            return progress
        state = self._store.get_personal_state(media_id)
        if state is not None and state.status in {
            LibraryStatus.UP_TO_DATE,
            LibraryStatus.COMPLETED,
        }:
            self._tracker.change_status(media_id, LibraryStatus.IN_PROGRESS)
        return progress

    def mark_season_unseen(self, media_id: str, season_number: int) -> EpisodeProgress:
        catalog = self._catalog_for(media_id)
        if catalog is None:
            return self._tracker.get_episode_progress(media_id)
        progress = self._tracker.get_episode_progress(media_id)
        for episode in catalog.episodes:
            if episode.season_number != season_number:
                continue
            reference = EpisodeRef(episode.season_number, episode.episode_number)
            while progress.has_seen(reference):
                progress = self.mark_episode_unseen(media_id, reference)
        return progress

    def _reject_future_episode(self, media_id: str, reference: EpisodeRef) -> None:
        catalog = self._catalog_for(media_id)
        if catalog is None:
            return
        episode = next(
            (
                candidate
                for candidate in catalog.episodes
                if candidate.season_number == reference.season_number
                and candidate.episode_number == reference.episode_number
            ),
            None,
        )
        if episode is None or episode.airdate is None:
            return
        if episode.airdate > (self._today or date.today()):
            raise ValueError("cannot mark a future episode as seen")

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
