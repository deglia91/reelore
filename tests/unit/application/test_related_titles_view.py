from reelore.application.catalog import TVSeriesCatalog
from reelore.application.related import RelatedTVTitle
from reelore.application.related_view import RelatedTitleViewService


class StubRelatedProvider:
    def related_to(self, catalog: TVSeriesCatalog) -> tuple[RelatedTVTitle, ...]:
        assert catalog.title == "Loki"
        return (
            RelatedTVTitle(
                provider_key="88396",
                title="The Falcon and the Winter Soldier",
                image_url="https://img.example/falcon.jpg",
            ),
            RelatedTVTitle(provider_key="92749", title="Moon Knight"),
        )


class FailingRelatedProvider:
    def related_to(self, catalog: TVSeriesCatalog) -> tuple[RelatedTVTitle, ...]:
        raise RuntimeError("provider unavailable")


def _catalog() -> TVSeriesCatalog:
    return TVSeriesCatalog(
        provider_id="1",
        title="Loki",
        summary=None,
        status="Ended",
        premiered=None,
        ended=None,
        image_url=None,
    )


def test_related_title_view_service_exposes_provider_results() -> None:
    service = RelatedTitleViewService(StubRelatedProvider())

    related = service.list_for(_catalog())

    assert [item.title for item in related] == [
        "The Falcon and the Winter Soldier",
        "Moon Knight",
    ]
    assert related[0].provider_key == "88396"


def test_related_title_view_service_ignores_provider_failures() -> None:
    service = RelatedTitleViewService(FailingRelatedProvider())

    assert service.list_for(_catalog()) == ()
