"""Provider-independent localization boundary for TV metadata."""

from dataclasses import dataclass, replace
from typing import Protocol

from reelore.application.catalog import TVCatalogProvider, TVSearchResult, TVSeriesCatalog


@dataclass(frozen=True, slots=True)
class LocalizedEpisodeMetadata:
    season_number: int
    episode_number: int
    title: str | None = None
    summary: str | None = None


@dataclass(frozen=True, slots=True)
class LocalizedTVSeriesMetadata:
    title: str | None = None
    summary: str | None = None
    episodes: tuple[LocalizedEpisodeMetadata, ...] = ()


class TVMetadataLocalizer(Protocol):
    """Enrich provider-neutral TV metadata for one locale."""

    def localize(self, catalog: TVSeriesCatalog) -> LocalizedTVSeriesMetadata | None: ...


class LocalizedTVCatalogProvider:
    """Decorate a catalog provider with optional localized metadata."""

    def __init__(self, catalog_provider: TVCatalogProvider, localizer: TVMetadataLocalizer) -> None:
        self._catalog_provider = catalog_provider
        self._localizer = localizer

    def search(self, query: str) -> tuple[TVSearchResult, ...]:
        return self._catalog_provider.search(query)

    def get_series(self, provider_id: str) -> TVSeriesCatalog:
        catalog = self._catalog_provider.get_series(provider_id)
        localized = self._localizer.localize(catalog)
        if localized is None:
            return catalog

        localized_episodes = {
            (episode.season_number, episode.episode_number): episode
            for episode in localized.episodes
        }
        episodes = tuple(
            replace(
                episode,
                title=(localized_episode.title if localized_episode else None) or episode.title,
                summary=(localized_episode.summary if localized_episode else None)
                or episode.summary,
            )
            for episode in catalog.episodes
            for localized_episode in [
                localized_episodes.get((episode.season_number, episode.episode_number))
            ]
        )
        return replace(
            catalog,
            title=localized.title or catalog.title,
            summary=localized.summary or catalog.summary,
            episodes=episodes,
        )
