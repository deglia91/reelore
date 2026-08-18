"""Composition root for the local Reelore web application."""

import os
from pathlib import Path

from fastapi import FastAPI

from reelore.application import MediaTracker, TVCatalogImporter
from reelore.application.catalog import TVCatalogProvider
from reelore.application.library_view import LibraryViewService
from reelore.application.localization import LocalizedTVCatalogProvider
from reelore.application.tracker import TVProgressTracker
from reelore.infrastructure import SQLiteLibraryRepository, TMDBItalianLocalizer, TVMazeProvider
from reelore.web import create_web_app

_DEFAULT_DATABASE_PATH = "data/reelore.db"


def build_app(database_path: str | Path, *, tmdb_token: str | None = None) -> FastAPI:
    path = Path(database_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    repository = SQLiteLibraryRepository(path)
    repository.initialize()
    tracker = MediaTracker(repository)
    catalog_provider: TVCatalogProvider = TVMazeProvider()
    if tmdb_token:
        catalog_provider = LocalizedTVCatalogProvider(
            catalog_provider,
            TMDBItalianLocalizer(tmdb_token),
        )
    importer = TVCatalogImporter(
        catalog_provider,
        repository,
        tracker,
        provider_name="tvmaze",
    )
    views = LibraryViewService(repository)
    tv_progress = TVProgressTracker(tracker, repository)
    return create_web_app(importer, views, tv_progress)


def build_default_app() -> FastAPI:
    database_path = os.environ.get("REELORE_DB_PATH", _DEFAULT_DATABASE_PATH)
    tmdb_token = os.environ.get("TMDB_API_TOKEN")
    return build_app(database_path, tmdb_token=tmdb_token)
