"""Curated explicit franchise relationships keyed by source provider IDs."""

from collections.abc import Mapping

from reelore.application.catalog import TVSeriesCatalog
from reelore.application.franchise import FranchiseTVTitle


class CuratedFranchiseTVProvider:
    """Read known franchise relationships without inferring them from similarity data."""

    def __init__(self, graph: Mapping[str, tuple[FranchiseTVTitle, ...]]) -> None:
        self._graph = dict(graph)

    def franchise_for(self, catalog: TVSeriesCatalog) -> tuple[FranchiseTVTitle, ...]:
        return self._graph.get(catalog.provider_id, ())
