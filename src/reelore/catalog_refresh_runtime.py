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


class ReleaseReminderRunner(Protocol):
    def run(self, today: date) -> int: ...


def start_catalog_refresh(
    service: CatalogRefresher,
    reconciliation: TVStatusReconciler | None = None,
    reminders: ReleaseReminderRunner | None = None,
) -> Thread:
    """Refresh catalog, reconcile tracking state, then run due reminders."""

    def refresh_and_reconcile() -> None:
        service.refresh_library()
        today = date.today()
        if reconciliation is not None:
            reconciliation.reconcile(today)
        if reminders is not None:
            reminders.run(today)

    thread = Thread(
        target=refresh_and_reconcile,
        name="reelore-catalog-refresh",
        daemon=True,
    )
    thread.start()
    return thread
