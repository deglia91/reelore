"""Application-layer ports and use cases for Reelore."""

from reelore.application.catalog import (
    TVCastMember,
    TVCatalogProvider,
    TVEpisodeMetadata,
    TVSearchResult,
    TVSeriesCatalog,
)
from reelore.application.catalog_import import ImportedTVSeries, TVCatalogImporter, TVCatalogStore
from reelore.application.library import LibraryRepository
from reelore.application.tracker import MediaNotFoundError, MediaTracker, TopTenService
from reelore.application.watch_history import GlobalWatchHistoryReader, WatchHistoryRepository

__all__ = [
    "GlobalWatchHistoryReader",
    "ImportedTVSeries",
    "LibraryRepository",
    "MediaNotFoundError",
    "MediaTracker",
    "TVCastMember",
    "TVCatalogImporter",
    "TVCatalogProvider",
    "TVCatalogStore",
    "TVEpisodeMetadata",
    "TVSearchResult",
    "TVSeriesCatalog",
    "TopTenService",
    "WatchHistoryRepository",
]
