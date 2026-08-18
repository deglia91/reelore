"""Application service for importing TV catalog entries into the local library."""

from dataclasses import dataclass
from typing import Protocol

from reelore.application.catalog import TVCatalogProvider, TVSearchResult, TVSeriesCatalog
from reelore.application.tracker import MediaTracker
from reelore.domain import LibraryStatus, MediaItem, MediaType


class TVCatalogStore(Protocol):
    """Persist provider-neutral TV catalog metadata locally."""

    def save_tv_series_catalog(self, catalog: TVSeriesCatalog) -> None: ...

    def get_tv_series_catalog(self, provider_id: str) -> TVSeriesCatalog | None: ...


@dataclass(frozen=True, slots=True)
class ImportedTVSeries:
    media_id: str
    catalog: TVSeriesCatalog


class TVCatalogImporter:
    """Search a provider and import selected TV metadata into Reelore."""

    def __init__(
        self,
        provider: TVCatalogProvider,
        catalog_store: TVCatalogStore,
        tracker: MediaTracker,
        *,
        provider_name: str,
    ) -> None:
        self._provider = provider
        self._catalog_store = catalog_store
        self._tracker = tracker
        self._provider_name = provider_name.strip().lower()
        if not self._provider_name:
            raise ValueError("provider name cannot be empty")

    def search(self, query: str) -> tuple[TVSearchResult, ...]:
        return self._provider.search(query)

    def import_series(
        self,
        provider_id: str,
        status: LibraryStatus = LibraryStatus.PLANNED,
    ) -> ImportedTVSeries:
        catalog = self._provider.get_series(provider_id)
        media_id = f"{self._provider_name}:{catalog.provider_id}"
        self._tracker.add_media(
            MediaItem(id=media_id, title=catalog.title, media_type=MediaType.TV_SERIES),
            status=status,
        )
        self._catalog_store.save_tv_series_catalog(catalog)
        return ImportedTVSeries(media_id=media_id, catalog=catalog)
