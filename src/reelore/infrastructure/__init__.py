"""Infrastructure adapters for Reelore."""

from reelore.infrastructure.sqlite_library import SQLiteLibraryRepository
from reelore.infrastructure.sqlite_watch_history import SQLiteWatchHistoryRepository
from reelore.infrastructure.tmdb import TMDBItalianLocalizer, TMDBLocalizerError
from reelore.infrastructure.tvmaze import TVMazeProvider, TVMazeProviderError

__all__ = [
    "SQLiteLibraryRepository",
    "SQLiteWatchHistoryRepository",
    "TMDBItalianLocalizer",
    "TMDBLocalizerError",
    "TVMazeProvider",
    "TVMazeProviderError",
]
