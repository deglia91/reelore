"""Runtime helper for refreshing cached TV metadata without blocking app startup."""

from datetime import date
from threading import Thread
from typing import Protocol

from reelore.application.catalog_refresh import CatalogRefreshResult
from reelore.application.tv_status_reconciliation import TVStatusReconciliationResult


class CatalogRefresher(Protocol):
    def refresh_library(self) -> CatalogRefreshResult: ...


class TVStatusReconciler(Protocol):
    def reconcile(self, today: date) -> TVStatusReconciliationResult: ...


def start_catalog_refresh(
    service: CatalogRefresher,
    reconciliation: TVStatusReconciler | None = None,
) -> Thread:
    """Refresh the local catalog in a daemon thread and reconcile tracking state."""

    def refresh_and_reconcile() -> None:
        service.refresh_library()
        if reconciliation is not None:
            reconciliation.reconcile(date.today())

    thread = Thread(
        target=refresh_and_reconcile,
        name="reelore-catalog-refresh",
        daemon=True,
    )
    thread.start()
    return thread
