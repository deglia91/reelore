"""Runtime helper for refreshing cached TV metadata without blocking app startup."""

from threading import Thread

from reelore.application.catalog_refresh import TVCatalogRefreshService


def start_catalog_refresh(service: TVCatalogRefreshService) -> Thread:
    """Refresh the local catalog in a daemon thread and return the running task."""

    thread = Thread(
        target=service.refresh_library,
        name="reelore-catalog-refresh",
        daemon=True,
    )
    thread.start()
    return thread
