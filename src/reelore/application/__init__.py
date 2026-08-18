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
from reelore.application.localization import (
    LocalizedEpisodeMetadata,
    LocalizedTVCatalogProvider,
    LocalizedTVSeriesMetadata,
    TVMetadataLocalizer,
)
from reelore.application.tracker import MediaNotFoundError, MediaTracker

__all__ = [
    "ImportedTVSeries",
    "LibraryRepository",
    "LocalizedEpisodeMetadata",
    "LocalizedTVCatalogProvider",
    "LocalizedTVSeriesMetadata",
    "MediaNotFoundError",
    "MediaTracker",
    "TVCastMember",
    "TVCatalogImporter",
    "TVCatalogProvider",
    "TVCatalogStore",
    "TVEpisodeMetadata",
    "TVMetadataLocalizer",
    "TVSearchResult",
    "TVSeriesCatalog",
]
