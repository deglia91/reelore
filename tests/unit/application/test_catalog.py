from reelore.application import TVCatalogProvider, TVSearchResult, TVSeriesCatalog


class StubCatalogProvider:
    def search(self, query: str) -> tuple[TVSearchResult, ...]:
        return (TVSearchResult(provider_id="123", title=query),)

    def get_series(self, provider_id: str) -> TVSeriesCatalog:
        raise NotImplementedError


def _accept_provider(provider: TVCatalogProvider) -> None:
    assert provider.search("Severance")[0].provider_id == "123"


def test_catalog_provider_is_structural() -> None:
    _accept_provider(StubCatalogProvider())
