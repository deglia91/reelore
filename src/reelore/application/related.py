"""Provider-independent related TV title boundary."""

from dataclasses import dataclass
from datetime import date
from typing import Protocol

from reelore.application.catalog import TVSeriesCatalog


@dataclass(frozen=True, slots=True)
class RelatedTVTitle:
    provider_key: str
    title: str
    premiered: date | None = None
    summary: str | None = None
    image_url: str | None = None


class RelatedTVProvider(Protocol):
    """Return provider-ranked TV titles related to a source series."""

    def related_to(self, catalog: TVSeriesCatalog) -> tuple[RelatedTVTitle, ...]: ...
