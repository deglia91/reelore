"""Read models for rendering the personal TV library."""

from dataclasses import dataclass
from datetime import date
from typing import Protocol

from reelore.application.availability import SeasonAvailability, TVAvailabilityProvider
from reelore.application.catalog import TVSeriesCatalog
from reelore.domain import EpisodeProgress, EpisodeRef, LibraryStatus, MediaItem, PersonalMediaState


class LibraryViewStore(Protocol):
    def list_media(self) -> tuple[MediaItem, ...]: ...

    def get_personal_state(self, media_id: str) -> PersonalMediaState | None: ...

    def get_episode_progress(self, media_id: str) -> EpisodeProgress: ...

    def get_tv_series_catalog(self, provider_id: str) -> TVSeriesCatalog | None: ...


@dataclass(frozen=True, slots=True)
class NextEpisodeView:
    season_number: int
    episode_number: int
    title: str


@dataclass(frozen=True, slots=True)
class LibraryItemView:
    media_id: str
    title: str
    status: LibraryStatus
    completion_count: int
    rewatch_count: int
    image_url: str | None
    seen_episodes: int
    total_episodes: int
    next_episode: NextEpisodeView | None = None


@dataclass(frozen=True, slots=True)
class UpcomingEpisodeView:
    media_id: str
    series_title: str
    season_number: int
    episode_number: int
    episode_title: str
    airdate: date
    image_url: str | None
    availability: SeasonAvailability | None = None


@dataclass(frozen=True, slots=True)
class TVSeriesDetailView:
    media_id: str
    state: PersonalMediaState
    progress: EpisodeProgress
    catalog: TVSeriesCatalog
    availability: tuple[SeasonAvailability, ...] = ()


class LibraryViewService:
    """Combine local tracking state with cached provider metadata for presentation."""

    def __init__(
        self,
        store: LibraryViewStore,
        availability_provider: TVAvailabilityProvider | None = None,
    ) -> None:
        self._store = store
        self._availability_provider = availability_provider

    def list_items(self, today: date | None = None) -> tuple[LibraryItemView, ...]:
        current_date = today or date.today()
        items: list[LibraryItemView] = []
        for media in self._store.list_media():
            state = self._store.get_personal_state(media.id)
            if state is None:
                continue
            catalog = self._catalog_for(media.id)
            progress = self._store.get_episode_progress(media.id)
            items.append(
                LibraryItemView(
                    media_id=media.id,
                    title=media.title,
                    status=state.status,
                    completion_count=state.completion_count,
                    rewatch_count=state.rewatch_count,
                    image_url=catalog.image_url if catalog is not None else None,
                    seen_episodes=progress.seen_count,
                    total_episodes=len(catalog.episodes) if catalog is not None else 0,
                    next_episode=self._next_episode(catalog, progress, current_date),
                )
            )
        return tuple(items)

    def list_upcoming_episodes(self, today: date) -> tuple[UpcomingEpisodeView, ...]:
        upcoming: list[UpcomingEpisodeView] = []
        excluded = {LibraryStatus.DROPPED, LibraryStatus.COMPLETED}
        for media in self._store.list_media():
            state = self._store.get_personal_state(media.id)
            catalog = self._catalog_for(media.id)
            if state is None or catalog is None or state.status in excluded:
                continue
            availability_by_season: dict[int, SeasonAvailability | None] = {}
            for episode in catalog.episodes:
                if episode.airdate is None or episode.airdate < today:
                    continue
                if episode.season_number not in availability_by_season:
                    availability_by_season[episode.season_number] = self._season_availability(
                        catalog,
                        episode.season_number,
                    )
                upcoming.append(
                    UpcomingEpisodeView(
                        media_id=media.id,
                        series_title=media.title,
                        season_number=episode.season_number,
                        episode_number=episode.episode_number,
                        episode_title=episode.title,
                        airdate=episode.airdate,
                        image_url=episode.image_url or catalog.image_url,
                        availability=availability_by_season[episode.season_number],
                    )
                )
        return tuple(sorted(upcoming, key=lambda episode: episode.airdate))

    def get_tv_series(self, media_id: str) -> TVSeriesDetailView | None:
        state = self._store.get_personal_state(media_id)
        catalog = self._catalog_for(media_id)
        if state is None or catalog is None:
            return None
        return TVSeriesDetailView(
            media_id=media_id,
            state=state,
            progress=self._store.get_episode_progress(media_id),
            catalog=catalog,
            availability=self._availability_for(catalog),
        )

    def _next_episode(
        self,
        catalog: TVSeriesCatalog | None,
        progress: EpisodeProgress,
        today: date,
    ) -> NextEpisodeView | None:
        if catalog is None:
            return None
        available = sorted(
            (
                episode
                for episode in catalog.episodes
                if episode.airdate is None or episode.airdate <= today
            ),
            key=lambda episode: (episode.season_number, episode.episode_number),
        )
        for episode in available:
            reference = EpisodeRef(episode.season_number, episode.episode_number)
            if not progress.has_seen(reference):
                return NextEpisodeView(
                    season_number=episode.season_number,
                    episode_number=episode.episode_number,
                    title=episode.title,
                )
        return None

    def _availability_for(self, catalog: TVSeriesCatalog) -> tuple[SeasonAvailability, ...]:
        availability = (
            self._season_availability(catalog, season_number)
            for season_number in sorted({episode.season_number for episode in catalog.episodes})
        )
        return tuple(season for season in availability if season is not None)

    def _season_availability(
        self,
        catalog: TVSeriesCatalog,
        season_number: int,
    ) -> SeasonAvailability | None:
        if self._availability_provider is None:
            return None
        try:
            return self._availability_provider.season_availability(
                catalog,
                season_number,
                "IT",
            )
        except Exception:
            return None

    def _catalog_for(self, media_id: str) -> TVSeriesCatalog | None:
        provider_id = _tvmaze_provider_id(media_id)
        if provider_id is None:
            return None
        return self._store.get_tv_series_catalog(provider_id)


def _tvmaze_provider_id(media_id: str) -> str | None:
    prefix, separator, provider_id = media_id.partition(":")
    if separator and prefix == "tvmaze" and provider_id:
        return provider_id
    return None
