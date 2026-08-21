"""Application service for explicit TV franchise relationships."""

from reelore.application.catalog import TVSeriesCatalog
from reelore.application.franchise import FranchiseTVProvider, FranchiseTVTitle


class FranchiseTitleViewService:
    """Read franchise titles without letting provider failures break presentation."""

    def __init__(self, franchise_provider: FranchiseTVProvider) -> None:
        self._franchise_provider = franchise_provider

    def list_for(self, catalog: TVSeriesCatalog) -> tuple[FranchiseTVTitle, ...]:
        try:
            return self._franchise_provider.franchise_for(catalog)
        except Exception:
            return ()
