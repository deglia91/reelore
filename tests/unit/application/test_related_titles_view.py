from reelore.application.catalog import TVSeriesCatalog
from reelore.application.library_view import LibraryViewService
from reelore.application.related import RelatedTVTitle
from reelore.domain import EpisodeProgress, LibraryStatus, MediaItem, MediaType, PersonalMediaState


class StubStore:
    def list_media(self) -> tuple[MediaItem, ...]:
        return (MediaItem("tvmaze:1", "Loki", MediaType.TV_SERIES),)

    def get_personal_state(self, media_id: str) -> PersonalMediaState | None:
        return PersonalMediaState(media_id, LibraryStatus.COMPLETED)

    def get_episode_progress(self, media_id: str) -> EpisodeProgress:
        return EpisodeProgress(media_id)

    def get_tv_series_catalog(self, provider_id: str) -> TVSeriesCatalog | None:
        assert provider_id == "1"
        return TVSeriesCatalog(
            provider_id="1",
            title="Loki",
            summary=None,
            status="Ended",
            premiered=None,
            ended=None,
            image_url=None,
        )


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


def test_series_detail_exposes_provider_related_titles() -> None:
    service = LibraryViewService(StubStore(), related_provider=StubRelatedProvider())

    detail = service.get_tv_series("tvmaze:1")

    assert detail is not None
    assert [item.title for item in detail.related_titles] == [
        "The Falcon and the Winter Soldier",
        "Moon Knight",
    ]
    assert detail.related_titles[0].provider_key == "88396"


def test_series_detail_ignores_related_provider_failures() -> None:
    service = LibraryViewService(StubStore(), related_provider=FailingRelatedProvider())

    detail = service.get_tv_series("tvmaze:1")

    assert detail is not None
    assert detail.related_titles == ()
