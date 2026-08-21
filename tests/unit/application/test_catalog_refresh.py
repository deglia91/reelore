from datetime import date

from reelore.application.catalog import TVSeriesCatalog
from reelore.application.catalog_refresh import TVCatalogRefreshService
from reelore.domain import MediaItem, MediaType


class StubProvider:
    def __init__(
        self, catalogs: dict[str, TVSeriesCatalog], failing: set[str] | None = None
    ) -> None:
        self._catalogs = catalogs
        self._failing = failing or set()
        self.requested: list[str] = []

    def get_series(self, provider_id: str) -> TVSeriesCatalog:
        self.requested.append(provider_id)
        if provider_id in self._failing:
            raise RuntimeError("provider unavailable")
        return self._catalogs[provider_id]


class StubStore:
    def __init__(self, media: tuple[MediaItem, ...]) -> None:
        self._media = media
        self.saved: list[TVSeriesCatalog] = []

    def list_media(self) -> tuple[MediaItem, ...]:
        return self._media

    def save_tv_series_catalog(self, catalog: TVSeriesCatalog) -> None:
        self.saved.append(catalog)


def _catalog(provider_id: str, title: str) -> TVSeriesCatalog:
    return TVSeriesCatalog(
        provider_id=provider_id,
        title=title,
        summary=None,
        status="Running",
        premiered=date(2020, 1, 1),
        ended=None,
        image_url=None,
    )


def test_refresh_library_updates_existing_tv_catalogs_without_touching_other_media() -> None:
    updated = _catalog("1", "Updated series")
    provider = StubProvider({"1": updated})
    store = StubStore(
        (
            MediaItem("tvmaze:1", "Old series", MediaType.TV_SERIES),
            MediaItem("other:2", "Other series", MediaType.TV_SERIES),
            MediaItem("tvmaze:3", "A film", MediaType.FILM),
        )
    )
    service = TVCatalogRefreshService(provider, store, provider_name="tvmaze")

    result = service.refresh_library()

    assert provider.requested == ["1"]
    assert store.saved == [updated]
    assert result.refreshed == 1
    assert result.failed == 0


def test_refresh_library_continues_when_one_provider_request_fails() -> None:
    updated = _catalog("2", "Second series")
    provider = StubProvider({"2": updated}, failing={"1"})
    store = StubStore(
        (
            MediaItem("tvmaze:1", "First series", MediaType.TV_SERIES),
            MediaItem("tvmaze:2", "Second series", MediaType.TV_SERIES),
        )
    )
    service = TVCatalogRefreshService(provider, store, provider_name="tvmaze")

    result = service.refresh_library()

    assert provider.requested == ["1", "2"]
    assert store.saved == [updated]
    assert result.refreshed == 1
    assert result.failed == 1
