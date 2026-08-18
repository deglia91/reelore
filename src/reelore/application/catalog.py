"""Provider-independent TV catalog boundary."""

from dataclasses import dataclass
from datetime import date
from typing import Protocol


@dataclass(frozen=True, slots=True)
class TVSearchResult:
    provider_id: str
    title: str
    premiered: date | None = None
    status: str | None = None
    image_url: str | None = None


@dataclass(frozen=True, slots=True)
class TVEpisodeMetadata:
    provider_id: str
    season_number: int
    episode_number: int
    title: str
    airdate: date | None = None
    summary: str | None = None
    image_url: str | None = None


@dataclass(frozen=True, slots=True)
class TVCastMember:
    person_name: str
    character_name: str
    image_url: str | None = None


@dataclass(frozen=True, slots=True)
class TVSeriesCatalog:
    provider_id: str
    title: str
    summary: str | None
    status: str | None
    premiered: date | None
    ended: date | None
    image_url: str | None
    episodes: tuple[TVEpisodeMetadata, ...] = ()
    cast: tuple[TVCastMember, ...] = ()


class TVCatalogProvider(Protocol):
    """Search and retrieve TV metadata without exposing provider-specific models."""

    def search(self, query: str) -> tuple[TVSearchResult, ...]: ...

    def get_series(self, provider_id: str) -> TVSeriesCatalog: ...
