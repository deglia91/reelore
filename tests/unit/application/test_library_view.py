from datetime import date, datetime

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
    EpisodeWatch,
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
                    airdate=date(2026, 8, 17),
                    image_url="https://img.example/episode.jpg",
                ),
                TVEpisodeMetadata("13", 1, 3, "Future", airdate=date(2026, 8, 20)),
            ),
        )


class MultiSeasonViewStore(StubViewStore):
    def get_episode_progress(self, media_id: str) -> EpisodeProgress:
        progress = EpisodeProgress(media_id)
        for episode_number in range(1, 4):
            progress = progress.mark_seen(EpisodeRef(2, episode_number))
        return progress

    def get_tv_series_catalog(self, provider_id: str) -> TVSeriesCatalog | None:
        assert provider_id == "1"
        episodes = tuple(
            TVEpisodeMetadata(f"1{number}", 1, number, f"S1 Episode {number}")
            for number in range(1, 8)
        ) + tuple(
            TVEpisodeMetadata(f"2{number}", 2, number, f"S2 Episode {number}")
            for number in range(1, 11)
        )
        return TVSeriesCatalog(
            provider_id="1",
            title="Example",
            summary="Summary",
            status="Running",
            premiered=None,
            ended=None,
            image_url="https://img.example/poster.jpg",
            episodes=episodes,
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


class StubWatchHistory:
    def list_episode_watches(self, media_id: str) -> tuple[EpisodeWatch, ...]:
        watched_at = datetime(2026, 8, 18, 20, 30)
        return (
            EpisodeWatch(media_id, EpisodeRef(1, 1), watched_at),
            EpisodeWatch(media_id, EpisodeRef(1, 1), watched_at),
            EpisodeWatch(media_id, EpisodeRef(1, 2), watched_at),
        )


class ScatteredRewatchHistory:
    def list_episode_watches(self, media_id: str) -> tuple[EpisodeWatch, ...]:
        watched_at = datetime(2026, 8, 18, 20, 30)
        return (
            EpisodeWatch(media_id, EpisodeRef(1, 1), watched_at),
            EpisodeWatch(media_id, EpisodeRef(1, 2), watched_at),
            EpisodeWatch(media_id, EpisodeRef(1, 2), watched_at),
        )


def test_library_view_combines_catalog_tracking_and_next_episode_data() -> None:
    service = LibraryViewService(StubViewStore(), StubAvailabilityProvider())

    item = service.list_items(date(2026, 8, 18))[0]
    detail = service.get_tv_series("tvmaze:1")

    assert item.image_url == "https://img.example/poster.jpg"
    assert item.status is LibraryStatus.IN_PROGRESS
    assert item.seen_episodes == 1
    assert item.total_episodes == 2
    assert item.rewatch_count == 1
    assert item.next_episode is not None
    assert item.next_episode.season_number == 1
    assert item.next_episode.episode_number == 2
    assert item.next_episode.title == "Second"
    assert detail is not None
    assert detail.catalog.title == "Example"
    assert detail.progress.has_seen(EpisodeRef(1, 1))
    assert detail.availability[0].providers[0].name == "Example Stream"
    assert detail.availability[0].source == "JustWatch"


def test_library_view_exposes_episode_watch_counts_from_history() -> None:
    service = LibraryViewService(
        StubViewStore(),
        StubAvailabilityProvider(),
        StubWatchHistory(),
    )

    detail = service.get_tv_series("tvmaze:1")

    assert detail is not None
    assert detail.watch_count(EpisodeRef(1, 1)) == 2
    assert detail.watch_count(EpisodeRef(1, 2)) == 1
    assert detail.watch_count(EpisodeRef(1, 3)) == 0


def test_library_view_derives_coherent_rewatch_progress_from_series_start() -> None:
    service = LibraryViewService(
        StubViewStore(),
        StubAvailabilityProvider(),
        StubWatchHistory(),
    )

    detail = service.get_tv_series("tvmaze:1")

    assert detail is not None
    assert detail.rewatch_progress is not None
    assert detail.rewatch_progress.pass_number == 2
    assert detail.rewatch_progress.watched_episodes == 1
    assert detail.rewatch_progress.total_episodes == 3
    assert detail.rewatch_progress.next_episode == EpisodeRef(1, 2)


def test_library_view_ignores_scattered_episode_rewatches() -> None:
    service = LibraryViewService(
        StubViewStore(),
        StubAvailabilityProvider(),
        ScatteredRewatchHistory(),
    )

    detail = service.get_tv_series("tvmaze:1")

    assert detail is not None
    assert detail.rewatch_progress is None


def test_library_view_exposes_progress_for_the_season_being_watched() -> None:
    service = LibraryViewService(MultiSeasonViewStore())

    item = service.list_items(date(2026, 8, 18))[0]

    assert item.current_season_progress is not None
    assert item.current_season_progress.season_number == 2
    assert item.current_season_progress.last_seen_episode_number == 3
    assert item.current_season_progress.seen_episodes == 3
    assert item.current_season_progress.total_episodes == 10
    assert item.next_episode is not None
    assert item.next_episode.season_number == 1
    assert item.next_episode.episode_number == 1


def test_library_view_lists_future_episodes_with_italian_availability() -> None:
    service = LibraryViewService(StubViewStore(), StubAvailabilityProvider())

    upcoming = service.list_upcoming_episodes(date(2026, 8, 18))

    assert len(upcoming) == 1
    assert upcoming[0].series_title == "Example"
    assert upcoming[0].season_number == 1
    assert upcoming[0].episode_number == 3
    assert upcoming[0].episode_title == "Future"
    assert upcoming[0].airdate == date(2026, 8, 20)
    assert upcoming[0].availability is not None
    assert upcoming[0].availability.providers[0].name == "Example Stream"
    assert upcoming[0].availability.source == "JustWatch"


def test_library_view_lists_recent_episodes_for_last_ninety_days_newest_first() -> None:
    service = LibraryViewService(StubViewStore(), StubAvailabilityProvider())

    recent = service.list_recent_episodes(date(2026, 8, 18))

    assert [episode.episode_number for episode in recent] == [2, 1]
    assert [episode.airdate for episode in recent] == [date(2026, 8, 17), date(2026, 8, 1)]
    assert recent[0].episode_title == "Second"
    assert recent[0].image_url == "https://img.example/episode.jpg"
    assert recent[0].availability is not None
    assert recent[0].availability.providers[0].name == "Example Stream"


def test_library_view_recent_episodes_respects_custom_window() -> None:
    service = LibraryViewService(StubViewStore())

    recent = service.list_recent_episodes(date(2026, 8, 18), days=7)

    assert len(recent) == 1
    assert recent[0].episode_number == 2
