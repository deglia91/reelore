"""Reconcile personal TV status when refreshed catalogs add new episodes."""

from dataclasses import dataclass
from datetime import date
from typing import Protocol

from reelore.application.catalog import TVSeriesCatalog
from reelore.domain import (
    EpisodeProgress,
    EpisodeRef,
    LibraryStatus,
    MediaItem,
    MediaType,
    PersonalMediaState,
)


class TVStatusReconciliationStore(Protocol):
    def list_media(self) -> tuple[MediaItem, ...]: ...

    def get_personal_state(self, media_id: str) -> PersonalMediaState | None: ...

    def get_episode_progress(self, media_id: str) -> EpisodeProgress: ...

    def get_tv_series_catalog(self, provider_id: str) -> TVSeriesCatalog | None: ...


class TVStatusUpdater(Protocol):
    def change_status(self, media_id: str, status: LibraryStatus) -> PersonalMediaState: ...


@dataclass(frozen=True, slots=True)
class TVStatusReconciliationResult:
    reopened: int


class TVStatusReconciliationService:
    """Reopen completed series when refreshed metadata introduces unseen episodes."""

    def __init__(
        self,
        store: TVStatusReconciliationStore,
        status_updater: TVStatusUpdater,
    ) -> None:
        self._store = store
        self._status_updater = status_updater

    def reconcile(self, today: date) -> TVStatusReconciliationResult:
        reopened = 0
        for media in self._store.list_media():
            if media.media_type is not MediaType.TV_SERIES:
                continue
            state = self._store.get_personal_state(media.id)
            if state is None or state.status is not LibraryStatus.COMPLETED:
                continue
            catalog = self._catalog_for(media.id)
            if catalog is None:
                continue
            progress = self._store.get_episode_progress(media.id)
            unseen = tuple(
                episode
                for episode in catalog.episodes
                if not progress.has_seen(EpisodeRef(episode.season_number, episode.episode_number))
            )
            if not unseen:
                continue
            has_available_unseen = any(
                episode.airdate is None or episode.airdate <= today for episode in unseen
            )
            status = (
                LibraryStatus.IN_PROGRESS if has_available_unseen else LibraryStatus.UP_TO_DATE
            )
            self._status_updater.change_status(media.id, status)
            reopened += 1
        return TVStatusReconciliationResult(reopened=reopened)

    def _catalog_for(self, media_id: str) -> TVSeriesCatalog | None:
        _prefix, separator, provider_id = media_id.partition(":")
        if not separator or not provider_id:
            return None
        return self._store.get_tv_series_catalog(provider_id)
