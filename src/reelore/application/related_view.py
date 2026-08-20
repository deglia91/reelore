"""Application service for provider-ranked related TV titles."""

from reelore.application.catalog import TVSeriesCatalog
from reelore.application.related import RelatedTVProvider, RelatedTVTitle


class RelatedTitleViewService:
    """Read related titles without letting provider failures break presentation."""

    def __init__(self, related_provider: RelatedTVProvider) -> None:
        self._related_provider = related_provider

    def list_for(self, catalog: TVSeriesCatalog) -> tuple[RelatedTVTitle, ...]:
        try:
            return self._related_provider.related_to(catalog)
        except Exception:
            return ()
