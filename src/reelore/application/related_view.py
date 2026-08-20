"""Related-title enrichment for the personal library detail view."""

from reelore.application.library_view import LibraryViewService, TVSeriesDetailView
from reelore.application.related import RelatedTVProvider, RelatedTVTitle


class RelatedLibraryViewService:
    """Decorate library views with provider-ranked related titles."""

    def __init__(self, views: LibraryViewService, related_provider: RelatedTVProvider) -> None:
        self._views = views
        self._related_provider = related_provider

    def __getattr__(self, name: str) -> object:
        return getattr(self._views, name)

    def get_tv_series(self, media_id: str) -> TVSeriesDetailView | None:
        detail = self._views.get_tv_series(media_id)
        if detail is None:
            return None
        return detail

    def related_titles(self, detail: TVSeriesDetailView) -> tuple[RelatedTVTitle, ...]:
        try:
            return self._related_provider.related_to(detail.catalog)
        except Exception:
            return ()
