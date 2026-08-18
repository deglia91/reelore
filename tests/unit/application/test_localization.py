from reelore.application.catalog import TVEpisodeMetadata, TVSearchResult, TVSeriesCatalog
from reelore.application.localization import (
    LocalizedEpisodeMetadata,
    LocalizedTVCatalogProvider,
    LocalizedTVSeriesMetadata,
)


class StubCatalogProvider:
    def __init__(self, catalog: TVSeriesCatalog) -> None:
        self.catalog = catalog

    def search(self, query: str) -> tuple[TVSearchResult, ...]:
        return ()

    def get_series(self, provider_id: str) -> TVSeriesCatalog:
        return self.catalog


class StubLocalizer:
    def __init__(self, localized: LocalizedTVSeriesMetadata | None) -> None:
        self.localized = localized

    def localize(self, catalog: TVSeriesCatalog) -> LocalizedTVSeriesMetadata | None:
        return self.localized


def _catalog() -> TVSeriesCatalog:
    return TVSeriesCatalog(
        provider_id="16740",
        title="Severance",
        summary="English summary",
        status="Running",
        premiered=None,
        ended=None,
        image_url=None,
        episodes=(
            TVEpisodeMetadata(
                provider_id="2001",
                season_number=1,
                episode_number=1,
                title="Good News About Hell",
                summary="English episode summary",
            ),
        ),
    )


def test_localized_catalog_uses_translation_and_falls_back_per_field() -> None:
    provider = LocalizedTVCatalogProvider(
        StubCatalogProvider(_catalog()),
        StubLocalizer(
            LocalizedTVSeriesMetadata(
                title="Scissione",
                summary=None,
                episodes=(
                    LocalizedEpisodeMetadata(
                        season_number=1,
                        episode_number=1,
                        title="Buone notizie sull'inferno",
                        summary=None,
                    ),
                ),
            )
        ),
    )

    series = provider.get_series("16740")

    assert series.title == "Scissione"
    assert series.summary == "English summary"
    assert series.episodes[0].title == "Buone notizie sull'inferno"
    assert series.episodes[0].summary == "English episode summary"


def test_localized_catalog_returns_original_when_localizer_has_no_match() -> None:
    catalog = _catalog()
    provider = LocalizedTVCatalogProvider(StubCatalogProvider(catalog), StubLocalizer(None))

    assert provider.get_series("16740") == catalog
