"""Composition root for the local Reelore web application."""

import os
from pathlib import Path

from fastapi import FastAPI

from reelore.application import MediaTracker, TVCatalogImporter
from reelore.infrastructure import SQLiteLibraryRepository, TVMazeProvider
from reelore.web import create_web_app

_DEFAULT_DATABASE_PATH = "data/reelore.db"


def build_app(database_path: str | Path) -> FastAPI:
    path = Path(database_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    repository = SQLiteLibraryRepository(path)
    repository.initialize()
    tracker = MediaTracker(repository)
    importer = TVCatalogImporter(
        TVMazeProvider(),
        repository,
        tracker,
        provider_name="tvmaze",
    )
    return create_web_app(importer, repository)


def build_default_app() -> FastAPI:
    database_path = os.environ.get("REELORE_DB_PATH", _DEFAULT_DATABASE_PATH)
    return build_app(database_path)
