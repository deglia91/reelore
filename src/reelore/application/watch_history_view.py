"""Read model for chronological episode watch history."""

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

from reelore.application.catalog import TVSeriesCatalog
from reelore.application.watch_history import GlobalWatchHistoryReader
from reelore.domain import EpisodeRef, MediaItem


class WatchHistoryViewStore(Protocol):
    def list_media(self) -> tuple[MediaItem, ...]: ...

    def get_tv_series_catalog(self, provider_id: str) -> TVSeriesCatalog | None: ...


@dataclass(frozen=True, slots=True)
class WatchHistoryItemView:
    media_id: str
    series_title: str
    season_number: int
    episode_number: int
    episode_title: str
    watched_at: datetime | None
    watch_number: int


class WatchHistoryViewService:
    """Enrich active watch records with local catalog metadata for presentation."""

    def __init__(
        self,
        store: WatchHistoryViewStore,
        history: GlobalWatchHistoryReader,
    ) -> None:
        self._store = store
        self._history = history

    def list_history(self) -> tuple[WatchHistoryItemView, ...]:
        media_by_id = {media.id: media for media in self._store.list_media()}
        counts: dict[tuple[str, EpisodeRef], int] = {}
        items: list[WatchHistoryItemView] = []
        for watch in self._history.list_all_episode_watches():
            media = media_by_id.get(watch.media_id)
            provider_id = _provider_id(watch.media_id)
            if media is None or provider_id is None:
                continue
            catalog = self._store.get_tv_series_catalog(provider_id)
            if catalog is None:
                continue
            episode_title = _episode_title(catalog, watch.episode)
            if episode_title is None:
                continue
            key = (watch.media_id, watch.episode)
            watch_number = counts.get(key, 0) + 1
            counts[key] = watch_number
            items.append(
                WatchHistoryItemView(
                    media_id=watch.media_id,
                    series_title=media.title,
                    season_number=watch.episode.season_number,
                    episode_number=watch.episode.episode_number,
                    episode_title=episode_title,
                    watched_at=watch.watched_at,
                    watch_number=watch_number,
                )
            )
        items.reverse()
        return tuple(items)


def _provider_id(media_id: str) -> str | None:
    _, separator, provider_id = media_id.partition(":")
    if not separator or not provider_id:
        return None
    return provider_id


def _episode_title(catalog: TVSeriesCatalog, reference: EpisodeRef) -> str | None:
    for episode in catalog.episodes:
        if (
            episode.season_number == reference.season_number
            and episode.episode_number == reference.episode_number
        ):
            return episode.title
    return None
