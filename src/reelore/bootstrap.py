"""Composition root for the local Reelore web application."""

import os
import sys
from pathlib import Path

from fastapi import FastAPI

from reelore.application import MediaTracker, TopTenService, TVCatalogImporter
from reelore.application.catalog import TVCatalogProvider
from reelore.application.catalog_refresh import TVCatalogRefreshService
from reelore.application.franchise_view import FranchiseTitleViewService
from reelore.application.library_view import LibraryViewService
from reelore.application.localization import LocalizedTVCatalogProvider
from reelore.application.related_view import RelatedTitleViewService
from reelore.application.release_reminders import ReleaseReminderDeliveryService
from reelore.application.tracker import TVProgressTracker
from reelore.application.tv_status_reconciliation import TVStatusReconciliationService
from reelore.application.watch_history_view import WatchHistoryViewService
from reelore.catalog_refresh_runtime import start_catalog_refresh
from reelore.infrastructure import (
    SQLiteLibraryRepository,
    SQLiteWatchHistoryRepository,
    TMDBItalianLocalizer,
    TVMazeProvider,
)
from reelore.infrastructure.curated_franchise import (
    CURATED_TV_FRANCHISE_GRAPH,
    CuratedFranchiseTVProvider,
)
from reelore.infrastructure.macos_notifications import MacOSReleaseReminderNotifier
from reelore.infrastructure.sqlite_release_reminder_preferences import (
    SQLiteReleaseReminderPreferences,
)
from reelore.infrastructure.sqlite_release_reminders import SQLiteReleaseReminderHistory
from reelore.infrastructure.tmdb_availability import TMDBItalianAvailabilityProvider
from reelore.infrastructure.tmdb_related import TMDBRelatedTVProvider
from reelore.release_reminder_runtime import ReleaseReminderRuntime
from reelore.release_reminder_scheduler import start_release_reminder_scheduler
from reelore.web import create_web_app
from reelore.web_history import install_history_routes
from reelore.web_release_reminders import install_release_reminder_routes
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
    reminder_preferences = SQLiteReleaseReminderPreferences(path)
    reminder_preferences.initialize()
    tracker = MediaTracker(repository, watch_history)
    catalog_provider: TVCatalogProvider = TVMazeProvider()
    availability_provider = None
    related_views = None
    if tmdb_token:
        catalog_provider = LocalizedTVCatalogProvider(
            catalog_provider,
            TMDBItalianLocalizer(tmdb_token),
        )
        availability_provider = TMDBItalianAvailabilityProvider(tmdb_token)
        related_views = RelatedTitleViewService(TMDBRelatedTVProvider(tmdb_token))
    importer = TVCatalogImporter(
        catalog_provider,
        repository,
        tracker,
        provider_name="tvmaze",
    )
    refresh_service = TVCatalogRefreshService(
        catalog_provider,
        repository,
        provider_name="tvmaze",
    )
    reconciliation_service = TVStatusReconciliationService(repository, tracker)
    views = LibraryViewService(
        repository,
        availability_provider,
        watch_history,
    )
    notifications_available = sys.platform == "darwin"
    reminder_notifier: MacOSReleaseReminderNotifier | None = None
    reminder_runtime = None
    if notifications_available:
        reminder_history = SQLiteReleaseReminderHistory(path)
        reminder_history.initialize()
        reminder_notifier = MacOSReleaseReminderNotifier()
        reminder_delivery = ReleaseReminderDeliveryService(
            reminder_history,
            reminder_notifier,
        )
        reminder_runtime = ReleaseReminderRuntime(
            views,
            reminder_delivery,
            reminder_preferences,
        )
    franchise_views = FranchiseTitleViewService(
        CuratedFranchiseTVProvider(CURATED_TV_FRANCHISE_GRAPH)
    )
    history_views = WatchHistoryViewService(repository, watch_history)
    tv_progress = TVProgressTracker(tracker, repository)
    top_ten = TopTenService(repository)
    app = create_web_app(
        importer,
        views,
        tv_progress,
        top_ten,
        related_views,
        franchise_views,
    )
    install_history_routes(app, history_views)
    install_top_ten_routes(app, views, top_ten)
    install_release_reminder_routes(
        app,
        reminder_preferences,
        notifications_available=notifications_available,
        test_sender=reminder_notifier,
    )
    start_catalog_refresh(refresh_service, reconciliation_service, reminder_runtime)
    if reminder_runtime is not None:
        start_release_reminder_scheduler(reminder_runtime)
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
