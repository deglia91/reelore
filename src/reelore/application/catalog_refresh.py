"""Refresh locally cached TV catalog metadata for media already in the library."""

from dataclasses import dataclass
from typing import Protocol

from reelore.application.catalog import TVCatalogProvider, TVSeriesCatalog
from reelore.domain import MediaItem, MediaType


class TVCatalogRefreshStore(Protocol):
    """Read tracked media and persist refreshed TV catalog metadata."""

    def list_media(self) -> tuple[MediaItem, ...]: ...

    def save_tv_series_catalog(self, catalog: TVSeriesCatalog) -> None: ...


@dataclass(frozen=True, slots=True)
class CatalogRefreshResult:
    refreshed: int
    failed: int


class TVCatalogRefreshService:
    """Refresh provider metadata without changing personal tracking state."""

    def __init__(
        self,
        provider: TVCatalogProvider,
        store: TVCatalogRefreshStore,
        *,
        provider_name: str,
    ) -> None:
        self._provider = provider
        self._store = store
        self._provider_name = provider_name.strip().lower()
        if not self._provider_name:
            raise ValueError("provider name cannot be empty")

    def refresh_library(self) -> CatalogRefreshResult:
        refreshed = 0
        failed = 0
        prefix = f"{self._provider_name}:"
        for media in self._store.list_media():
            if media.media_type is not MediaType.TV_SERIES or not media.id.startswith(prefix):
                continue
            provider_id = media.id.removeprefix(prefix)
            if not provider_id:
                continue
            try:
                catalog = self._provider.get_series(provider_id)
            except Exception:
                failed += 1
                continue
            self._store.save_tv_series_catalog(catalog)
            refreshed += 1
        return CatalogRefreshResult(refreshed=refreshed, failed=failed)
