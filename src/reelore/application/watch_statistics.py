"""Aggregate watch activity into provider-neutral personal statistics."""

from dataclasses import dataclass
from typing import Protocol

from reelore.application.catalog import TVSeriesCatalog
from reelore.application.watch_history import GlobalWatchHistoryReader
from reelore.domain import EpisodeRef


class WatchStatisticsStore(Protocol):
    def get_tv_series_catalog(self, provider_id: str) -> TVSeriesCatalog | None: ...


@dataclass(frozen=True, slots=True)
class WatchStatistics:
    total_watch_minutes: int
    total_watches: int
    unique_episodes: int
    rewatches: int


class WatchStatisticsService:
    """Calculate personal watch statistics from authoritative watch history."""

    def __init__(
        self,
        store: WatchStatisticsStore,
        history: GlobalWatchHistoryReader,
    ) -> None:
        self._store = store
        self._history = history

    def get_statistics(self) -> WatchStatistics:
        watches = self._history.list_all_episode_watches()
        unique = {(watch.media_id, watch.episode) for watch in watches}
        total_minutes = sum(self._runtime_minutes(watch.media_id, watch.episode) for watch in watches)
        return WatchStatistics(
            total_watch_minutes=total_minutes,
            total_watches=len(watches),
            unique_episodes=len(unique),
            rewatches=len(watches) - len(unique),
        )

    def _runtime_minutes(self, media_id: str, reference: EpisodeRef) -> int:
        provider_id = _provider_id(media_id)
        if provider_id is None:
            return 0
        catalog = self._store.get_tv_series_catalog(provider_id)
        if catalog is None:
            return 0
        for episode in catalog.episodes:
            if (
                episode.season_number == reference.season_number
                and episode.episode_number == reference.episode_number
            ):
                return episode.runtime_minutes or 0
        return 0


def _provider_id(media_id: str) -> str | None:
    _, separator, provider_id = media_id.partition(":")
    if not separator or not provider_id:
        return None
    return provider_id
