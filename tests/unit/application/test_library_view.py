from datetime import date

from reelore.application import TVEpisodeMetadata, TVSeriesCatalog
from reelore.application.availability import (
    AvailabilityProvider,
    AvailabilityType,
    SeasonAvailability,
)
from reelore.application.library_view import LibraryViewService
from reelore.domain import (
    EpisodeProgress,
    EpisodeRef,
    LibraryStatus,
    MediaItem,
    MediaType,
    PersonalMediaState,
)


class StubViewStore:
    def list_media(self) -> tuple[MediaItem, ...]:
        return (MediaItem("tvmaze:1", "Example", MediaType.TV_SERIES),)

    def get_personal_state(self, media_id: str) -> PersonalMediaState | None:
        return PersonalMediaState(media_id, LibraryStatus.IN_PROGRESS, completion_count=2)

    def get_episode_progress(self, media_id: str) -> EpisodeProgress:
        return EpisodeProgress(media_id).mark_seen(EpisodeRef(1, 1))

    def get_tv_series_catalog(self, provider_id: str) -> TVSeriesCatalog | None:
        assert provider_id == "1"
        return TVSeriesCatalog(
            provider_id="1",
            title="Example",
            summary="Summary",
            status="Running",
            premiered=None,
            ended=None,
            image_url="https://img.example/poster.jpg",
            episodes=(
                TVEpisodeMetadata("11", 1, 1, "Pilot", airdate=date(2026, 8, 1)),
                TVEpisodeMetadata(
                    "12",
                    1,
                    2,
                    "Second",
                    airdate=date(2026, 8, 20),
                    image_url="https://img.example/episode.jpg",
                ),
            ),
        )


class StubAvailabilityProvider:
    def season_availability(
        self,
        catalog: TVSeriesCatalog,
        season_number: int,
        region: str,
    ) -> SeasonAvailability | None:
        assert catalog.provider_id == "1"
        assert region == "IT"
        return SeasonAvailability(
            season_number=season_number,
            region=region,
            providers=(AvailabilityProvider("Example Stream", AvailabilityType.STREAM),),
            source="JustWatch",
            source_url="https://example.test/watch",
        )


def test_library_view_combines_catalog_tracking_and_rewatch_data() -> None:
    service = LibraryViewService(StubViewStore(), StubAvailabilityProvider())

    item = service.list_items()[0]
    detail = service.get_tv_series("tvmaze:1")

    assert item.image_url == "https://img.example/poster.jpg"
    assert item.status is LibraryStatus.IN_PROGRESS
    assert item.seen_episodes == 1
    assert item.total_episodes == 2
    assert item.rewatch_count == 1
    assert detail is not None
    assert detail.catalog.title == "Example"
    assert detail.progress.has_seen(EpisodeRef(1, 1))
    assert detail.availability[0].providers[0].name == "Example Stream"
    assert detail.availability[0].source == "JustWatch"


def test_library_view_lists_future_episodes_in_airdate_order() -> None:
    service = LibraryViewService(StubViewStore())

    upcoming = service.list_upcoming_episodes(date(2026, 8, 18))

    assert len(upcoming) == 1
    assert upcoming[0].series_title == "Example"
    assert upcoming[0].season_number == 1
    assert upcoming[0].episode_number == 2
    assert upcoming[0].episode_title == "Second"
    assert upcoming[0].airdate == date(2026, 8, 20)
    assert upcoming[0].image_url == "https://img.example/episode.jpg"
