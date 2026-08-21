from datetime import date

from reelore.application import TVEpisodeMetadata, TVSeriesCatalog
from reelore.application.library_view import LibraryViewService
from reelore.domain import EpisodeProgress, EpisodeRef, LibraryStatus, MediaItem, MediaType, PersonalMediaState


class ReturningSeriesStore:
    def list_media(self) -> tuple[MediaItem, ...]:
        return (MediaItem("tvmaze:1", "Returning", MediaType.TV_SERIES),)

    def get_personal_state(self, media_id: str) -> PersonalMediaState | None:
        return PersonalMediaState(media_id, LibraryStatus.COMPLETED, completion_count=1)

    def get_episode_progress(self, media_id: str) -> EpisodeProgress:
        return EpisodeProgress(media_id).mark_seen(EpisodeRef(2, 1))

    def get_tv_series_catalog(self, provider_id: str) -> TVSeriesCatalog | None:
        return TVSeriesCatalog(
            provider_id=provider_id,
            title="Returning",
            summary=None,
            status="Running",
            premiered=None,
            ended=None,
            image_url=None,
            episodes=(
                TVEpisodeMetadata("21", 2, 1, "Known future", airdate=date(2026, 9, 1)),
                TVEpisodeMetadata("31", 3, 1, "New season", airdate=date(2026, 10, 1)),
            ),
        )


def test_completed_series_returns_to_calendar_when_refresh_adds_unseen_future_episode() -> None:
    service = LibraryViewService(ReturningSeriesStore())

    upcoming = service.list_upcoming_episodes(date(2026, 8, 21))

    assert [(item.season_number, item.episode_number) for item in upcoming] == [(3, 1)]
    assert upcoming[0].episode_title == "New season"
