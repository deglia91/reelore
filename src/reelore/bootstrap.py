"""Composition root for the local Reelore web application."""

import os
from pathlib import Path

from fastapi import FastAPI

from reelore.application import MediaTracker, TopTenService, TVCatalogImporter
from reelore.application.catalog import TVCatalogProvider
from reelore.application.library_view import LibraryViewService
from reelore.application.localization import LocalizedTVCatalogProvider
from reelore.application.tracker import TVProgressTracker
from reelore.application.watch_history_view import WatchHistoryViewService
from reelore.infrastructure import (
    SQLiteLibraryRepository,
    SQLiteWatchHistoryRepository,
    TMDBItalianLocalizer,
    TVMazeProvider,
)
from reelore.infrastructure.tmdb_availability import TMDBItalianAvailabilityProvider
from reelore.web import create_web_app
from reelore.web_history import install_history_routes
from reelore.web_top_ten import install_top_ten_routes

_DEFAULT_DATABASE_PATH = "data/reelore.db"
_DEFAULT_ENV_PATH = Path(".env")


def build_app(database_path: str | Path, *, tmdb_token: str | None = None) -> FastAPI:
    path = Path(database_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    repository = SQLiteLibraryRepository(path)
    repository.initialize()
    watch_history = SQLiteWatchHistoryRepository(path)
    watch_history.initialize()
    tracker = MediaTracker(repository, watch_history)
    catalog_provider: TVCatalogProvider = TVMazeProvider()
    availability_provider = None
    if tmdb_token:
        catalog_provider = LocalizedTVCatalogProvider(
            catalog_provider,
            TMDBItalianLocalizer(tmdb_token),
        )
        availability_provider = TMDBItalianAvailabilityProvider(tmdb_token)
    importer = TVCatalogImporter(
        catalog_provider,
        repository,
        tracker,
        provider_name="tvmaze",
    )
    views = LibraryViewService(
        repository,
        availability_provider,
        watch_history,
    )
    history_views = WatchHistoryViewService(repository, watch_history)
    tv_progress = TVProgressTracker(tracker, repository)
    top_ten = TopTenService(repository)
    app = create_web_app(importer, views, tv_progress, top_ten)
    install_history_routes(app, history_views)
    install_top_ten_routes(app, views, top_ten)
    return app


def build_default_app() -> FastAPI:
    _load_env_file(_DEFAULT_ENV_PATH)
    database_path = os.environ.get("REELORE_DB_PATH", _DEFAULT_DATABASE_PATH)
    tmdb_token = os.environ.get("TMDB_API_TOKEN")
    return build_app(database_path, tmdb_token=tmdb_token)


def _load_env_file(path: Path) -> None:
    if not path.is_file():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, raw_value = line.split("=", 1)
        key = key.strip()
        if not key:
            continue
        value = raw_value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
            value = value[1:-1]
        os.environ.setdefault(key, value)
