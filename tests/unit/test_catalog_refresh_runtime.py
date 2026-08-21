from threading import Event

from reelore.application.catalog_refresh import CatalogRefreshResult
from reelore.catalog_refresh_runtime import start_catalog_refresh


class StubRefreshService:
    def __init__(self) -> None:
        self.called = Event()

    def refresh_library(self) -> CatalogRefreshResult:
        self.called.set()
        return CatalogRefreshResult(refreshed=1, failed=0)


def test_catalog_refresh_starts_in_background_daemon_thread() -> None:
    service = StubRefreshService()

    thread = start_catalog_refresh(service)  # type: ignore[arg-type]

    assert thread.daemon is True
    assert thread.name == "reelore-catalog-refresh"
    assert service.called.wait(timeout=1)
