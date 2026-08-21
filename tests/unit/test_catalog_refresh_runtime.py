from datetime import date
from threading import Event

from reelore.application.catalog_refresh import CatalogRefreshResult
from reelore.application.tv_status_reconciliation import TVStatusReconciliationResult
from reelore.catalog_refresh_runtime import start_catalog_refresh


class StubRefreshService:
    def __init__(self, calls: list[str] | None = None) -> None:
        self.called = Event()
        self.calls = calls

    def refresh_library(self) -> CatalogRefreshResult:
        if self.calls is not None:
            self.calls.append("refresh")
        self.called.set()
        return CatalogRefreshResult(refreshed=1, failed=0)


class StubReconciliationService:
    def __init__(self, calls: list[str]) -> None:
        self.calls = calls
        self.called = Event()

    def reconcile(self, today: date) -> TVStatusReconciliationResult:
        self.calls.append("reconcile")
        self.called.set()
        return TVStatusReconciliationResult(reopened=1)


def test_catalog_refresh_starts_in_background_daemon_thread() -> None:
    service = StubRefreshService()

    thread = start_catalog_refresh(service)

    assert thread.daemon is True
    assert thread.name == "reelore-catalog-refresh"
    assert service.called.wait(timeout=1)


def test_catalog_refresh_reconciles_tv_status_after_refresh() -> None:
    calls: list[str] = []
    refresh = StubRefreshService(calls)
    reconciliation = StubReconciliationService(calls)

    thread = start_catalog_refresh(refresh, reconciliation)
    thread.join(timeout=1)

    assert reconciliation.called.is_set()
    assert calls == ["refresh", "reconcile"]
