"""Curated explicit franchise relationships keyed by source provider IDs."""

from collections.abc import Mapping
from datetime import date
from types import MappingProxyType

from reelore.application.catalog import TVSeriesCatalog
from reelore.application.franchise import FranchiseRelationType, FranchiseTVTitle


CURATED_TV_FRANCHISE_GRAPH: Mapping[str, tuple[FranchiseTVTitle, ...]] = MappingProxyType(
    {
        "169": (
            FranchiseTVTitle(
                provider_key="618",
                title="Better Call Saul",
                relations=(
                    FranchiseRelationType.SPIN_OFF_OF,
                    FranchiseRelationType.PREQUEL_OF,
                ),
                premiered=date(2015, 2, 8),
            ),
        ),
        "618": (
            FranchiseTVTitle(
                provider_key="169",
                title="Breaking Bad",
                relations=(FranchiseRelationType.SAME_UNIVERSE,),
                premiered=date(2008, 1, 20),
            ),
        ),
        "82": (
            FranchiseTVTitle(
                provider_key="44778",
                title="House of the Dragon",
                relations=(
                    FranchiseRelationType.PREQUEL_OF,
                    FranchiseRelationType.SAME_UNIVERSE,
                ),
                premiered=date(2022, 8, 21),
            ),
        ),
        "44778": (
            FranchiseTVTitle(
                provider_key="82",
                title="Game of Thrones",
                relations=(
                    FranchiseRelationType.SEQUEL_OF,
                    FranchiseRelationType.SAME_UNIVERSE,
                ),
                premiered=date(2011, 4, 17),
            ),
        ),
    }
)


class CuratedFranchiseTVProvider:
    """Read known franchise relationships without inferring them from similarity data."""

    def __init__(self, graph: Mapping[str, tuple[FranchiseTVTitle, ...]]) -> None:
        self._graph = dict(graph)

    def franchise_for(self, catalog: TVSeriesCatalog) -> tuple[FranchiseTVTitle, ...]:
        return self._graph.get(catalog.provider_id, ())
