"""Provider-independent regional availability models for TV content."""

from dataclasses import dataclass
from enum import StrEnum
from typing import Protocol

from reelore.application.catalog import TVSeriesCatalog


class AvailabilityType(StrEnum):
    STREAM = "stream"
    FREE = "free"
    ADS = "ads"
    RENT = "rent"
    BUY = "buy"


@dataclass(frozen=True, slots=True)
class AvailabilityProvider:
    name: str
    availability_type: AvailabilityType
    logo_url: str | None = None


@dataclass(frozen=True, slots=True)
class SeasonAvailability:
    season_number: int
    region: str
    providers: tuple[AvailabilityProvider, ...]
    source: str
    source_url: str | None = None


class TVAvailabilityProvider(Protocol):
    """Resolve regional availability without exposing upstream provider models."""

    def season_availability(
        self,
        catalog: TVSeriesCatalog,
        season_number: int,
        region: str,
    ) -> SeasonAvailability | None: ...
