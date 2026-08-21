"""Provider-independent franchise and narrative-universe boundary."""

from dataclasses import dataclass
from datetime import date
from enum import StrEnum
from typing import Protocol

from reelore.application.catalog import TVSeriesCatalog


class FranchiseRelationType(StrEnum):
    """Describe an explicit narrative relationship between TV titles."""

    PREQUEL_OF = "prequel_of"
    SEQUEL_OF = "sequel_of"
    SPIN_OFF_OF = "spin_off_of"
    SAME_UNIVERSE = "same_universe"
    CHARACTER_RELATED = "character_related"
    RECOMMENDED_BEFORE = "recommended_before"
    RECOMMENDED_AFTER = "recommended_after"


@dataclass(frozen=True, slots=True)
class FranchiseTVTitle:
    """TV title with explicit franchise relationships to a source series."""

    provider_key: str
    title: str
    relations: tuple[FranchiseRelationType, ...]
    premiered: date | None = None
    summary: str | None = None
    image_url: str | None = None


class FranchiseTVProvider(Protocol):
    """Return titles with explicit franchise relationships to a source series."""

    def franchise_for(self, catalog: TVSeriesCatalog) -> tuple[FranchiseTVTitle, ...]: ...
