"""Runtime helper for refreshing cached TV metadata without blocking app startup."""

from threading import Thread
from typing import Protocol

from reelore.application.catalog_refresh import CatalogRefreshResult


class CatalogRefresher(Protocol):
    def refresh_library(self) -> CatalogRefreshResult: ...


def start_catalog_refresh(service: CatalogRefresher) -> Thread:
    """Refresh the local catalog in a daemon thread and return the running task."""

    thread = Thread(
        target=service.refresh_library,
        name="reelore-catalog-refresh",
        daemon=True,
    )
    thread.start()
    return thread
